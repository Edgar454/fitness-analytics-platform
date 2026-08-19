import os
import ssl
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DB_USER = os.environ.get("DB_USER")
    CERT_PATH = os.environ.get("CERT_PATH")

    # asyncpg : pas de sslmode/sslrootcert en query string (contrairement à
    # psycopg2) — il faut construire un ssl.SSLContext et le passer via
    # connect_args au moment de create_async_engine().
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+asyncpg://{DB_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:5432/sportfolio"
    )

    @classmethod
    def get_ssl_connect_args(cls) -> dict:
        ssl_context = ssl.create_default_context(cafile=cls.CERT_PATH)
        return {"ssl": ssl_context}