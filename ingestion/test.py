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

from src.connectors.google_health.auth import GoogleAuthConnector
from src.connectors.google_health.neat_connector import GoogleHealthNeatConnector

load_dotenv()

auth = GoogleAuthConnector(
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
)

connector = GoogleHealthNeatConnector(auth=auth)

# fenêtre large pour être sûr d'attraper au moins une pesée existante
until = datetime.utcnow()
since = until - timedelta(days=90)

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