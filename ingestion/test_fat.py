from datetime import date
from fatsecret import Fatsecret
import os
from dotenv import load_dotenv

load_dotenv()

fs = Fatsecret(
    os.environ["FATSECRET_CONSUMER_KEY"],
    os.environ["FATSECRET_CONSUMER_SECRET"],
    session_token=(
        os.environ["FATSECRET_ACCESS_TOKEN"],
        os.environ["FATSECRET_ACCESS_TOKEN_SECRET"],
    ),
    auth="oauth1",
)

entries = fs.diary.entries_get_v2(date=date.today())

print(f"Entries: {len(entries)}")

for entry in entries:
    print(entry)