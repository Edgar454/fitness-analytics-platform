from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from ingestion.src.config import Config


from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)


class DatabaseConnector(ABC):

    @abstractmethod
    def get_engine(self):
        raise NotImplementedError

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        SessionLocal = async_sessionmaker(
            bind=self.get_engine(),
            expire_on_commit=False,
        )

        db = SessionLocal()

        try:
            yield db
            await db.commit()

        except Exception:
            await db.rollback()
            raise

        finally:
            await db.close()


class RDSConnector(DatabaseConnector):
    """
    ATTENTION : le driver change de psycopg2 (sync) à asyncpg (async).
    La connection string ET la gestion SSL doivent être adaptées :
      - schéma : postgresql+asyncpg:// (pas postgresql+psycopg2://)
      - asyncpg n'accepte pas sslmode/sslrootcert en query string comme
        psycopg2 — il faut passer un objet ssl.SSLContext via connect_args.
    Voir Config pour la construction de l'URL et du contexte SSL adaptés.
    """

    def __init__(self, database_url: str, connect_args: dict | None = None):
        self._database_url = database_url
        self._connect_args = connect_args or {}
        self._engine = None

    def get_engine(self):
        if self._engine is None:
            self._engine = create_async_engine(self._database_url, connect_args=self._connect_args)
        return self._engine



db_connector = RDSConnector(
    Config.SQLALCHEMY_DATABASE_URI,
    connect_args=Config.get_ssl_connect_args(),
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_connector.session() as db:
        yield db