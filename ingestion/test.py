"""
Test manuel du GoogleHealthBodyMeasurementConnector contre la vraie API.
Ne pas committer les credentials — utiliser .env comme pour la connexion DB.

Variables attendues dans .env :
  GOOGLE_CLIENT_ID
  GOOGLE_CLIENT_SECRET
  GOOGLE_REFRESH_TOKEN
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.connectors.fatsecret.auth import FatSecretAuthConnector
from src.connectors.fatsecret.nutrition_connector import FatSecretNutritionConnector

load_dotenv()

auth = FatSecretAuthConnector(
    consumer_key=os.environ["FATSECRET_CONSUMER_KEY"],
    consumer_secret=os.environ["FATSECRET_CONSUMER_SECRET"],
    access_token=os.environ["FATSECRET_ACCESS_TOKEN"],
    access_token_secret=os.environ["FATSECRET_ACCESS_TOKEN_SECRET"],
)


connector = FatSecretNutritionConnector(auth=auth)

# fenêtre large pour être sûr d'attraper au moins une pesée existante
until = datetime.utcnow()
since = until - timedelta(days=15)

print(f"Fetching raw data from {since.isoformat()} to {until.isoformat()}...")
raw = connector.fetch(since, until)
print(f"Raw points fetched: {len(raw)}")

if raw:
    print("\nSample raw point (first one):")
    print(raw[0])

records = connector.transform(raw)
print(f"\nTransformed records: {len(records)}")

for r in records[:10]:
    print(r)