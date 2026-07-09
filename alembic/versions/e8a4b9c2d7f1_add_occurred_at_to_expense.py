"""add_occurred_at_to_expense

Revision ID: e8a4b9c2d7f1
Revises: c2d91e4a6f10
Create Date: 2026-07-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e8a4b9c2d7f1"
down_revision: Union[str, None] = "c2d91e4a6f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("expense", sa.Column("occurred_at", sa.DateTime(), nullable=True))
    op.execute(
        """
        UPDATE expense
        SET occurred_at = COALESCE(created_at, date::timestamp)
        WHERE occurred_at IS NULL
        """
    )
    op.alter_column("expense", "occurred_at", nullable=False)


def downgrade() -> None:
    op.drop_column("expense", "occurred_at")
