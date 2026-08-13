from datetime import datetime, timedelta
import os

from src.config import Config
from src.database import RDSConnector
from src.connectors.lyfta.auth import LyftaAuthConnector
from src.connectors.lyfta.workout_connector import LyftaWorkoutConnector
from src.loaders.workout import load_workout_sessions

db_connector = RDSConnector(Config.SQLALCHEMY_DATABASE_URI)

auth = LyftaAuthConnector(api_key=os.environ["LYFTA_API_KEY"])
connector = LyftaWorkoutConnector(auth=auth)

until = datetime.utcnow()
since = until - timedelta(days=15)

print(f"Fetching from {since.isoformat()} to {until.isoformat()}...")
records = connector.run(since, until)
print(f"Records transformed: {len(records)}")

with db_connector.session() as db:
    written = load_workout_sessions(db, records)
    print(f"Sessions written to DB: {written}")