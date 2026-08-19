from datetime import datetime
import os

from src.config import Config
from src.database import RDSConnector

from src.connectors.lyfta.auth import LyftaAuthConnector
from src.connectors.lyfta.exercise_metadata import LyftaExerciseMetadataConnector
from src.loaders.workout import load_exercise_metadata
 
db_connector = RDSConnector(Config.SQLALCHEMY_DATABASE_URI)

auth = LyftaAuthConnector(api_key=os.environ["LYFTA_API_KEY"])
connector = LyftaExerciseMetadataConnector(auth=auth)

# since/until ignorés par ce connector, mais requis par la signature du contrat
now = datetime.utcnow()
records = connector.run(now, now)
print(f"Exercise metadata records fetched: {len(records)}")

if records:
    print("\nSample record:")
    print(records[0])

with db_connector.session() as db:
    updated = load_exercise_metadata(db, records)
    print(f"\nExercises updated: {updated}")