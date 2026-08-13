"""
Test manuel de /api/v1/exercises/progress, pour voir si les PRs y sont
documentés plus proprement que l'heuristique record_type is not None
sur /api/v1/workouts.
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["LYFTA_API_KEY"]
BASE_URL = "https://my.lyfta.app"

headers = {"Authorization": f"Bearer {API_KEY}"}

print("=== /api/v1/exercises/progress ===")
response = requests.get(f"{BASE_URL}/api/v1/exercises/progress", headers=headers, params={"limit": 10})
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

print("\n=== /api/v1/exercises/library (échantillon) ===")
response = requests.get(f"{BASE_URL}/api/v1/exercises/library", headers=headers, params={"limit": 5})
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))