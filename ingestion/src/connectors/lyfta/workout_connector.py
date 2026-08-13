from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional
import requests

from src.connectors.lyfta.auth import LyftaAuthConnector
from src.connectors.base_connector import BaseConnector
from src.connectors.models.workout_records import WorkoutSessionRecord, WorkoutSetRecord, WorkoutPrRecord

BASE_URL = "https://my.lyfta.app"


def _to_decimal(value: Optional[str]) -> Optional[Decimal]:
    if value is None or value == "":
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _to_int(value: Optional[str]) -> Optional[int]:
    dec = _to_decimal(value)
    return int(dec) if dec is not None else None


def _fix_double_escaped_unicode(value: Optional[str]) -> Optional[str]:
    """
    Certains champs texte de l'API Lyfta (ex: title) contiennent des séquences
    d'échappement Unicode doublement encodées (ex: 'Entra\\u00EEnement' avec un
    backslash littéral, au lieu du vrai caractère 'î') — bug apparent côté
    Lyfta, pas un problème de décodage JSON standard. On corrige en réinterprétant
    la chaîne comme unicode_escape.
    """
    if value is None:
        return None
    try:
        return value.encode("latin-1").decode("unicode_escape")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return value  # si le fix échoue, on garde la valeur brute plutôt que planter


# Sémantique de record_type déduite empiriquement en croisant plusieurs
# séances réelles (non documentée officiellement par Lyfta) :
#   "1" -> 1RM estimé (formule proche d'Epley : weight * (1 + reps/30))
#   "2" -> poids max (record_value == weight du set)
#   "3" -> volume max (record_value == weight * reps)
#   "4" -> reps max (record_value == reps du set)
# record_type/record_level/record_value sont des listes séparées par virgules
# quand un même set bat plusieurs records simultanément — ex: record_type="1,2",
# record_value="163,136.000" veut dire ce set a battu à la fois le record de
# 1RM estimé (163) ET le record de poids max (136).
RECORD_TYPE_METRIC = {
    "1": "estimated_1rm",
    "2": "max_weight",
    "3": "max_volume",
    "4": "max_reps",
}


class LyftaWorkoutConnector(BaseConnector[WorkoutSessionRecord]):
    """
    Connector workout s'appuyant sur l'API publique Lyfta (GET /api/v1/workouts,
    documentée, Bearer API key statique).

    Points non confirmés officiellement par la doc Lyfta, déduits empiriquement
    en croisant plusieurs séances réelles (cf. RECORD_TYPE_METRIC ci-dessus) :
      - record_type "1"/"2"/"3"/"4" -> 1RM estimé / poids max / volume max / reps max.
        Un même set peut battre plusieurs records à la fois (listes séparées
        par virgules dans record_type/record_value).
      - duration : absent de /workouts (seulement sur /workouts/summary),
        laissé à None pour l'instant plutôt que de faire un second appel.
    """

    connector_name = "lyfta"

    def __init__(self, auth: LyftaAuthConnector):
        self._auth = auth

    def fetch(self, since: datetime, until: datetime) -> list[dict]:
        workouts: list[dict] = []
        page = 1

        while True:
            response = requests.get(
                f"{BASE_URL}/api/v1/workouts",
                headers=self._auth.headers,
                params={"limit": 100, "page": page},
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()

            page_workouts = payload.get("workouts", [])
            if not page_workouts:
                break

            # Hypothèse : tri antichronologique (le plus récent en premier),
            # comportement le plus courant pour ce type d'API — NON confirmé
            # explicitement par la doc Lyfta. Si le tri s'avère être
            # chronologique (le plus ancien en premier), cette optimisation
            # est fausse et il faut revenir à une pagination complète.
            stop = False
            for workout in page_workouts:
                perform_date = datetime.strptime(workout["workout_perform_date"], "%Y-%m-%d %H:%M:%S")
                if perform_date < since:
                    stop = True
                    continue
                if perform_date <= until:
                    workouts.append(workout)

            if stop:
                break

            total_pages = payload.get("total_pages", 1)
            if page >= total_pages:
                break
            page += 1

        return workouts

    def transform(self, raw_data: list[dict]) -> list[WorkoutSessionRecord]:
        sessions: list[WorkoutSessionRecord] = []

        for workout in raw_data:
            performed_at = datetime.strptime(workout["workout_perform_date"], "%Y-%m-%d %H:%M:%S")

            sets: list[WorkoutSetRecord] = []
            prs: list[WorkoutPrRecord] = []

            for exercise in workout.get("exercises", []):
                exercise_name = exercise.get("excercise_name")  # faute de frappe côté API Lyfta
                if exercise_name is None:
                    continue
                exercise_name = _fix_double_escaped_unicode(exercise_name).strip()

                for i, raw_set in enumerate(exercise.get("sets", []), start=1):
                    weight = _to_decimal(raw_set.get("weight"))
                    reps = _to_int(raw_set.get("reps"))
                    rir = _to_decimal(raw_set.get("rir"))

                    # Certains types d'exercice (cardio: distance_duration) n'ont
                    # pas de weight/reps — on garde le set quand même, weight
                    # optionnel plutôt que de l'exclure.
                    sets.append(
                        WorkoutSetRecord(
                            exercise_name=exercise_name,
                            set_number=i,
                            weight=weight,
                            reps=reps,
                            is_warmup=None,  # pas de champ direct exposé par l'API
                            rir=rir,
                            performed_at=performed_at,
                        )
                    )

                    if raw_set.get("record_type") is not None:
                        types = str(raw_set["record_type"]).split(",")
                        values = str(raw_set.get("record_value", "")).split(",")

                        for record_type, raw_value in zip(types, values):
                            record_value = _to_decimal(raw_value.strip())
                            if record_value is None:
                                continue
                            metric = RECORD_TYPE_METRIC.get(record_type.strip())
                            if metric is None:
                                continue  # type de record inconnu, on ignore plutôt que deviner
                            prs.append(
                                WorkoutPrRecord(
                                    exercise_name=exercise_name,
                                    metric=metric,
                                    value=record_value,
                                    achieved_at=performed_at,
                                )
                            )

            sessions.append(
                WorkoutSessionRecord(
                    date=performed_at,
                    started_at=performed_at,
                    ended_at=None,
                    duration=None,
                    sources="lyfta",
                    notes=_fix_double_escaped_unicode(workout.get("title")),
                    sets=sets,
                    prs=prs,
                )
            )

        return sessions