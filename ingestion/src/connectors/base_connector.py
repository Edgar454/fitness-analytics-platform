from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class BaseConnector(ABC, Generic[T]):
    """
    Contrat commun à tous les connectors, tous domaines confondus.
    fetch -> transform -> run (le point d'entrée appelé par l'orchestrateur d'ingestion).
    """

    connector_name: str  

    @abstractmethod
    def fetch(self, since: datetime, until: datetime) -> list[dict]:
        """Récupère les données brutes depuis l'API tierce."""
        raise NotImplementedError

    @abstractmethod
    def transform(self, raw_data: list[dict]) -> list[T]:
        """Convertit les données brutes en instances de la dataclass de sortie du domaine."""
        raise NotImplementedError

    def run(self, since: datetime, until: datetime) -> list[T]:
        """Point d'entrée appelé par l'orchestrateur — identique pour tous les connectors."""
        raw_data = self.fetch(since, until)
        return self.transform(raw_data)