"""Add user_id to expensetracker

Revision ID: 3fa6dc0f5645
Revises: 90185bbb703e
Create Date: 2025-07-18 11:37:10.921279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fa6dc0f5645'
down_revision: Union[str, None] = '90185bbb703e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_id column to expensetracker table as nullable first
    op.add_column('expensetracker', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Handle existing data
    connection = op.get_bind()
    
    # Check if there are existing expense trackers
    result = connection.execute(sa.text("SELECT COUNT(*) FROM expensetracker"))
    count = result.scalar()
    
    if count > 0:
        # Check if default user exists, if not create it
        result = connection.execute(sa.text("SELECT id FROM users WHERE username = 'default_user'"))
        default_user_id = result.fetchone()
        
        if default_user_id is None:
            # Create a default user for existing data
            connection.execute(sa.text("""
                INSERT INTO users (username, email, hashed_password) 
                VALUES ('default_user', 'default@example.com', '$2b$12$defaulthashedpasswordforexistingdata')
            """))
            
            # Get the newly created default user ID
            result = connection.execute(sa.text("SELECT id FROM users WHERE username = 'default_user'"))
            default_user_id = result.scalar()
        else:
            default_user_id = default_user_id[0]
        
        # Update existing expense trackers with the default user
        connection.execute(sa.text(f"UPDATE expensetracker SET user_id = {default_user_id} WHERE user_id IS NULL"))
    
    # Now make the column non-nullable
    op.alter_column('expensetracker', 'user_id', nullable=False)
    
    # Add foreign key constraint
    op.create_foreign_key(None, 'expensetracker', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint(None, 'expensetracker', type_='foreignkey')
    
    # Remove user_id column
    op.drop_column('expensetracker', 'user_id')
