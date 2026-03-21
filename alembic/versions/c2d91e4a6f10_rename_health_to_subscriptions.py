"""rename_health_to_subscriptions

Revision ID: c2d91e4a6f10
Revises: b7c4f1b2e8aa
Create Date: 2026-03-21 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c2d91e4a6f10'
down_revision: Union[str, None] = 'b7c4f1b2e8aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE expense
        SET category = 'Subscriptions'
        WHERE category = 'Health'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE expense
        SET category = 'Health'
        WHERE category = 'Subscriptions'
        """
    )
