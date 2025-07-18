"""Add user authentication and relationships

Revision ID: 90185bbb703e
Revises: 
Create Date: 2025-07-18 11:35:25.467402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90185bbb703e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Add user_id column to expensetracker table as nullable first
    op.add_column('expensetracker', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Create a default user for existing expense trackers
    connection = op.get_bind()
    
    # Check if there are existing expense trackers
    result = connection.execute(sa.text("SELECT COUNT(*) FROM expensetracker"))
    count = result.scalar()
    
    if count > 0:
        # Create a default user for existing data
        connection.execute(sa.text("""
            INSERT INTO users (username, email, hashed_password) 
            VALUES ('default_user', 'default@example.com', '$2b$12$defaulthashedpasswordforexistingdata')
        """))
        
        # Get the default user ID
        result = connection.execute(sa.text("SELECT id FROM users WHERE username = 'default_user'"))
        default_user_id = result.scalar()
        
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
    
    # Drop indexes
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    
    # Drop users table
    op.drop_table('users')
