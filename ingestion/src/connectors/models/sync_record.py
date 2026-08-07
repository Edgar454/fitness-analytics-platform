from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class SyncStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"


class TriggerType(str, Enum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"


@dataclass(frozen=True)
class SyncResult:
    """
    Sortie produite par l'orchestrateur (pas par un connector individuel) après
    l'exécution d'un connector — sert directement à peupler sync_history.
    """

    connector: str
    started_at: datetime
    trigger_type: TriggerType
    ended_at: Optional[datetime] = None
    status: SyncStatus = SyncStatus.RUNNING
    records_processed: Optional[int] = None
    error: Optional[str] = None