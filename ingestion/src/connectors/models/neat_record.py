from dataclasses import dataclass
from datetime import date as date_
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class NeatRecord:
    """
    Sortie standardisée attendue de tout connector du domaine NEAT
    (activité non structurée : steps, sommeil, calories brûlées au quotidien).

    Modèle field-value plutôt qu'une ligne large par jour : chaque métrique
    est récupérée indépendamment via son propre appel dailyRollUp (structure
    de retour différente par type : StepsRollupValue, TotalCaloriesRollupValue,
    etc.), donc les combiner en une seule ligne par jour dans le connector
    forcerait une reconciliation entre types hétérogènes — source d'erreur si
    un type est absent/en retard un jour donné. On repousse cette reconciliation
    à la couche de présentation (dbt, pivot), où elle peut être faite une fois,
    correctement, sur des données déjà persistées.
    """

    date: date_
    metric_name: str  # ex: "steps", "sleep_minutes", "active_minutes", "calories_burned"
    value: Decimal
    unit: Optional[str] = None
    source: Optional[str] = None