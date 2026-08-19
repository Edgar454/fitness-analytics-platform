from dataclasses import dataclass
from datetime import date as date_
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class NeatRecord:
    """
    Sortie standardisée attendue de tout connector du domaine NEAT.
    Une instance = un jour agrégé, cohérent avec le contrat large des autres
    domaines (nutrition, etc.). Le pivot field-value -> large (nécessaire pour
    Google Health, qui fetch chaque métrique séparément via dailyRollUp) est
    interne au connector, pas exposé à l'appelant.
    """

    date: date_
    steps: Optional[int] = None
    active_minutes: Optional[int] = None
    distance: Optional[Decimal] = None
    calories_burned: Optional[Decimal] = None
    sleep_minutes: Optional[int] = None
    resting_hr: Optional[int] = None
    source: Optional[str] = None