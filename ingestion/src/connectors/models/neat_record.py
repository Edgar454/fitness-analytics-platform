from dataclasses import dataclass
from datetime import date as date_
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class NeatRecord:
    """
    Sortie standardisée attendue de tout connector du domaine NEAT
    (activité non structurée : steps, sommeil, calories brûlées au quotidien).
    Une instance = un jour agrégé, pas un micro-datapoint brut.
    """

    date: date_
    steps: Optional[int] = None
    active_minutes: Optional[int] = None
    distance: Optional[Decimal] = None
    calories_burned: Optional[Decimal] = None
    sleep_minutes: Optional[int] = None
    resting_hr: Optional[int] = None
    source: Optional[str] = None