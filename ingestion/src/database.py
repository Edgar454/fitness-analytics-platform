from abc import ABC, abstractmethod
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


class DatabaseConnector(ABC):
    """
    Contrat minimal pour toute implémentation de base de données —
    RDS aujourd'hui, Supabase demain, même interface.
    """

    @abstractmethod
    def get_engine(self):
        raise NotImplementedError

    @contextmanager
    def session(self) -> Session:
        """Fournit une session SQLAlchemy avec commit/rollback automatique."""
        SessionLocal = sessionmaker(bind=self.get_engine())
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


class RDSConnector(DatabaseConnector):
    def __init__(self, database_url: str):
        self._database_url = database_url
        self._engine = None

    def get_engine(self):
        if self._engine is None:
            self._engine = create_engine(self._database_url)
        return self._engine