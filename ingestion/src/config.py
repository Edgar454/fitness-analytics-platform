import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DB_USER = os.environ.get("DB_USER")
    CERT_PATH = os.environ.get("CERT_PATH")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:5432/sportfolio"
        f"?sslmode=verify-full&sslrootcert={CERT_PATH}"
    )