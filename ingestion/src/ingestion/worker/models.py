from dataclasses import dataclass
from typing import Awaitable, Callable, Any

from ingestion.src.connectors.base_connector import BaseConnector

@dataclass(frozen=True, slots=True)
class IngestionHandler:
    connector: BaseConnector
    loader: Callable[..., Awaitable[int]]