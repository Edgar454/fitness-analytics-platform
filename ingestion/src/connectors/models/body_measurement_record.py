from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class BodyMeasurementRecord:
    """
    Sortie standardisée attendue de tout connector du domaine body_measurement,
    indépendamment du provider (Google Health, Lyfta, etc.).
    Correspond à une seule mesure (un measure_type, une valeur, un instant donné).
    """

    measured_at: datetime
    measure_type_name: str  # ex: "bodyfat", "waist" — résolu vers measure_type.id au moment du load
    value: Decimal
    unit: Optional[str] = None
    source: Optional[str] = None