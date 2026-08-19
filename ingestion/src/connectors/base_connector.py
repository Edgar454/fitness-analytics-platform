from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class BaseConnector(ABC, Generic[T]):
    """
    Contrat commun à tous les connectors — version async.
    fetch/transform restent la même séparation, mais fetch() est maintenant
    une coroutine (I/O réseau), transform() reste synchrone (pur CPU, pas
    besoin d'async pour du parsing/mapping en mémoire).
    """

    connector_name: str

    @abstractmethod
    async def fetch(self, since: datetime, until: datetime) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def transform(self, raw_data: list[dict]) -> list[T]:
        raise NotImplementedError

    async def run(self, since: datetime, until: datetime) -> list[T]:
        raw_data = await self.fetch(since, until)
        return self.transform(raw_data)