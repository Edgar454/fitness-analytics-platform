"""
Seed des tables de référence equipment/body_part/muscle depuis le mapping
statique Lyfta (connectors/lyfta_mappings.py). Idempotent — utilise
ON CONFLICT DO NOTHING, peut être relancé sans dupliquer.

Usage: uv run seed_reference_tables.py
"""

from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.config import Config
from src.database import RDSConnector
from ingestion.src.models.fitness.reference import Equipment, BodyPart, Muscle
from src.connectors.lyfta.mappings import EQUIPMENT_BY_ID, BODY_PART_BY_ID, MUSCLE_BY_ID

db_connector = RDSConnector(Config.SQLALCHEMY_DATABASE_URI)


def seed_table(db, model, mapping: dict[str, str], label: str) -> int:
    count = 0
    for id_str, name in mapping.items():
        stmt = pg_insert(model).values(id=int(id_str), name=name).on_conflict_do_nothing(index_elements=["id"])
        result = db.execute(stmt)
        if result.rowcount > 0:
            count += 1
    print(f"[{label}] {count} nouvelles lignes insérées (sur {len(mapping)} au total)")
    return count


with db_connector.session() as db:
    seed_table(db, Equipment, EQUIPMENT_BY_ID, "equipment")
    seed_table(db, BodyPart, BODY_PART_BY_ID, "body_part")
    seed_table(db, Muscle, MUSCLE_BY_ID, "muscle")

print("Seed terminé.")