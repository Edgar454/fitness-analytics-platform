"""Migrated all the current tables in a fitness schema to separate them from the ingestion domain that only handles ingestion lifecycle

Revision ID: f85ff0b4fbef
Revises: 20efa1c35a28
Create Date: 2026-08-26 12:35:07.012713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f85ff0b4fbef'
down_revision: Union[str, Sequence[str], None] = '20efa1c35a28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS fitness")

    op.execute("ALTER TABLE public.body_part SET SCHEMA fitness")
    op.execute("ALTER TABLE public.equipment SET SCHEMA fitness")
    op.execute("ALTER TABLE public.exercise SET SCHEMA fitness")
    op.execute("ALTER TABLE public.measure_type SET SCHEMA fitness")
    op.execute("ALTER TABLE public.muscle SET SCHEMA fitness")
    op.execute("ALTER TABLE public.users SET SCHEMA fitness")
    op.execute("ALTER TABLE public.body_measurement SET SCHEMA fitness")
    op.execute("ALTER TABLE public.daily_health SET SCHEMA fitness")
    op.execute("ALTER TABLE public.daily_nutrition SET SCHEMA fitness")
    op.execute("ALTER TABLE public.daily_summary SET SCHEMA fitness")
    op.execute("ALTER TABLE public.progress_photos SET SCHEMA fitness")
    op.execute("ALTER TABLE public.sync_history SET SCHEMA fitness")
    op.execute("ALTER TABLE public.user_credentials SET SCHEMA fitness")
    op.execute("ALTER TABLE public.weekly_summary SET SCHEMA fitness")
    op.execute("ALTER TABLE public.workout_session SET SCHEMA fitness")
    op.execute("ALTER TABLE public.workout_pr SET SCHEMA fitness")
    op.execute("ALTER TABLE public.workout_set SET SCHEMA fitness")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE fitness.workout_set SET SCHEMA public")
    op.execute("ALTER TABLE fitness.workout_pr SET SCHEMA public")
    op.execute("ALTER TABLE fitness.workout_session SET SCHEMA public")
    op.execute("ALTER TABLE fitness.weekly_summary SET SCHEMA public")
    op.execute("ALTER TABLE fitness.user_credentials SET SCHEMA public")
    op.execute("ALTER TABLE fitness.sync_history SET SCHEMA public")
    op.execute("ALTER TABLE fitness.progress_photos SET SCHEMA public")
    op.execute("ALTER TABLE fitness.daily_summary SET SCHEMA public")
    op.execute("ALTER TABLE fitness.daily_nutrition SET SCHEMA public")
    op.execute("ALTER TABLE fitness.daily_health SET SCHEMA public")
    op.execute("ALTER TABLE fitness.body_measurement SET SCHEMA public")
    op.execute("ALTER TABLE fitness.users SET SCHEMA public")
    op.execute("ALTER TABLE fitness.muscle SET SCHEMA public")
    op.execute("ALTER TABLE fitness.measure_type SET SCHEMA public")
    op.execute("ALTER TABLE fitness.exercise SET SCHEMA public")
    op.execute("ALTER TABLE fitness.equipment SET SCHEMA public")
    op.execute("ALTER TABLE fitness.body_part SET SCHEMA public")

    op.execute("DROP SCHEMA fitness")