from dataclasses import dataclass
from datetime import date as date_
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class NutritionRecord:
    """
    Sortie standardisée attendue de tout connector du domaine nutrition
    (FatSecret, ou tout autre provider de suivi alimentaire).
    Une instance = un jour agrégé (total des repas/entrées de la journée).
    """

    date: date_
    calories: Optional[Decimal] = None
    protein: Optional[Decimal] = None
    fat: Optional[Decimal] = None
    carbs: Optional[Decimal] = None
    fiber: Optional[Decimal] = None
    water: Optional[Decimal] = None
    source: Optional[str] = None