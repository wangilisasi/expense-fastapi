"""rename_expense_categories

Revision ID: b7c4f1b2e8aa
Revises: 99ef13a4fd57
Create Date: 2026-03-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b7c4f1b2e8aa'
down_revision: Union[str, None] = '99ef13a4fd57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE expense
        SET category = 'Investing'
        WHERE category = 'Shopping'
        """
    )
    op.execute(
        """
        UPDATE expense
        SET category = 'Communications'
        WHERE category = 'Education'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE expense
        SET category = 'Shopping'
        WHERE category = 'Investing'
        """
    )
    op.execute(
        """
        UPDATE expense
        SET category = 'Education'
        WHERE category = 'Communications'
        """
    )
