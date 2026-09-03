"""Added the created status to job status 

Revision ID: 2fd9e8214667
Revises: 8ad6eba0ffdd
Create Date: 2026-09-03 09:24:33.456896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fd9e8214667'
down_revision: Union[str, Sequence[str], None] = '8ad6eba0ffdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE jobstatus ADD VALUE IF NOT EXISTS 'CREATED'"
    )


def downgrade() -> None:
    # PostgreSQL doesn't support removing an enum value directly.
    pass
