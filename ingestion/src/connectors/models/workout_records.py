from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class ExerciseMetadataRecord:
    """
    Sortie standardisée pour le domaine "métadonnées d'exercice" — catalogue,
    pas événementiel. Un ExerciseMetadataRecord = un exercice du catalogue
    Lyfta, avec ses IDs de référence (equipment/body_part/muscles) déjà
    parsés depuis les chaînes JSON-encodées de la réponse brute.
    """
 
    name: str
    image_url: Optional[str] = None
    equipment_ids: list[int] = field(default_factory=list)
    body_part_ids: list[int] = field(default_factory=list)
    target_muscle_ids: list[int] = field(default_factory=list)
    synergist_muscle_ids: list[int] = field(default_factory=list)
 


@dataclass(frozen=True)
class WorkoutSetRecord:
    """Un set individuel, rattaché à un seul exercice."""

    exercise_name: str
    set_number: int
    weight: Decimal
    reps: Optional[int] = None
    is_warmup: Optional[bool] = None
    rpe: Optional[Decimal] = None
    rir: Optional[Decimal] = None
    performed_at: Optional[datetime] = None


@dataclass(frozen=True)
class WorkoutPrRecord:
    """Un record personnel, rattaché à un exercice, indépendant de la structure des sets."""

    exercise_name: str
    metric: str
    value: Decimal
    achieved_at: datetime


@dataclass(frozen=True)
class WorkoutSessionRecord:
    """
    Sortie standardisée attendue de tout connector du domaine workout.
    Une instance = une séance complète, avec ses sets et ses éventuels PRs.
    """

    date: datetime
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None
    sources: Optional[str] = None
    notes: Optional[str] = None
    sets: list[WorkoutSetRecord] = field(default_factory=list)
    prs: list[WorkoutPrRecord] = field(default_factory=list)