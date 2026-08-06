from sqlalchemy import create_engine, text, inspect
from src.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
inspector = inspect(engine)

for table_name in inspector.get_table_names():
    print(table_name)