"""Add unique constraint on expense uuid_id for idempotent creation

Revision ID: a1b2c3d4e5f6
Revises: 756bc4ded82e
Create Date: 2026-02-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '756bc4ded82e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique constraint on expense.uuid_id to support idempotent creation
    # Note: uuid_id is already the primary key, which implies uniqueness in most databases.
    # This explicit unique constraint ensures the IntegrityError is raised consistently
    # across all database backends when a duplicate uuid_id is inserted.
    op.create_unique_constraint('expense_uuid_id_unique', 'expense', ['uuid_id'])


def downgrade() -> None:
    op.drop_constraint('expense_uuid_id_unique', 'expense', type_='unique')
