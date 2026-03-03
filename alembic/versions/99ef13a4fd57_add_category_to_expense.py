"""add_category_to_expense

Revision ID: 99ef13a4fd57
Revises: a1b2c3d4e5f6
Create Date: 2026-03-03 21:45:40.965390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99ef13a4fd57'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('expense', sa.Column('category', sa.String(), nullable=False, server_default='Other'))


def downgrade() -> None:
    op.drop_column('expense', 'category')
