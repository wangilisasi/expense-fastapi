"""Migrate to UUID primary keys

Revision ID: 4b2da278f535
Revises: 449996f77b27
Create Date: 2025-09-20 15:51:24.144317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b2da278f535'
down_revision: Union[str, None] = '449996f77b27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Drop all existing foreign key constraints that reference integer IDs
    op.drop_constraint('expense_trackerId_fkey', 'expense', type_='foreignkey')
    op.drop_constraint('expensetracker_user_id_fkey', 'expensetracker', type_='foreignkey')
    op.drop_constraint('refresh_tokens_user_id_fkey', 'refresh_tokens', type_='foreignkey')
    
    # Step 2: Update refresh_tokens to use UUID foreign key BEFORE dropping users.id
    # First add the UUID foreign key column
    op.add_column('refresh_tokens', sa.Column('uuid_user_id', sa.String(36), nullable=True))
    
    # Copy data from user_id to uuid_user_id using the users table (before dropping users.id)
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE refresh_tokens 
        SET uuid_user_id = users.uuid_id 
        FROM users 
        WHERE refresh_tokens.user_id = users.id
    """))
    
    # Make uuid_user_id non-nullable and drop old user_id
    op.alter_column('refresh_tokens', 'uuid_user_id', nullable=False)
    op.drop_column('refresh_tokens', 'user_id')
    
    # Step 3: Drop existing primary key constraints
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_constraint('expensetracker_pkey', 'expensetracker', type_='primary')  
    op.drop_constraint('expense_pkey', 'expense', type_='primary')
    
    # Step 4: Drop integer ID columns entirely (no backward compatibility)
    op.drop_column('users', 'id')
    op.drop_column('expensetracker', 'id')
    op.drop_column('expense', 'id')
    
    # Step 5: Drop old foreign key columns entirely
    op.drop_column('expensetracker', 'user_id')
    op.drop_column('expense', 'trackerId')
    
    # Step 6: Create new primary key constraints using UUIDs
    op.create_primary_key('users_pkey', 'users', ['uuid_id'])
    op.create_primary_key('expensetracker_pkey', 'expensetracker', ['uuid_id'])
    op.create_primary_key('expense_pkey', 'expense', ['uuid_id'])
    
    # Step 7: Create new foreign key constraints using UUIDs only
    op.create_foreign_key('expensetracker_uuid_user_id_fkey', 'expensetracker', 'users', ['uuid_user_id'], ['uuid_id'])
    op.create_foreign_key('expense_uuid_tracker_id_fkey', 'expense', 'expensetracker', ['uuid_tracker_id'], ['uuid_id'])
    op.create_foreign_key('refresh_tokens_uuid_user_id_fkey', 'refresh_tokens', 'users', ['uuid_user_id'], ['uuid_id'])


def downgrade() -> None:
    # This reverses the migration back to integer primary keys
    # WARNING: This will cause data loss for new records created after migration
    
    # Step 1: Drop UUID foreign key constraints
    op.drop_constraint('expense_uuid_tracker_id_fkey', 'expense', type_='foreignkey')
    op.drop_constraint('expensetracker_uuid_user_id_fkey', 'expensetracker', type_='foreignkey')
    op.drop_constraint('refresh_tokens_uuid_user_id_fkey', 'refresh_tokens', type_='foreignkey')
    
    # Step 2: Drop UUID primary key constraints
    op.drop_constraint('expense_pkey', 'expense', type_='primary')
    op.drop_constraint('expensetracker_pkey', 'expensetracker', type_='primary')
    op.drop_constraint('users_pkey', 'users', type_='primary')
    
    # Step 3: Add back integer ID columns as primary keys
    op.add_column('users', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    op.add_column('expensetracker', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    op.add_column('expense', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    
    # Step 4: Add back foreign key columns
    op.add_column('expensetracker', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('expense', sa.Column('trackerId', sa.Integer(), nullable=False))
    
    # Step 5: Create integer primary key constraints
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_primary_key('expensetracker_pkey', 'expensetracker', ['id'])
    op.create_primary_key('expense_pkey', 'expense', ['id'])
    
    # Step 6: Recreate integer foreign key constraints
    op.create_foreign_key('expensetracker_user_id_fkey', 'expensetracker', 'users', ['user_id'], ['id'])
    op.create_foreign_key('expense_trackerId_fkey', 'expense', 'expensetracker', ['trackerId'], ['id'])
    
    # Step 7: Update refresh_tokens back to integer foreign key
    op.add_column('refresh_tokens', sa.Column('user_id', sa.Integer(), nullable=False))
    op.drop_column('refresh_tokens', 'uuid_user_id')
    op.create_foreign_key('refresh_tokens_user_id_fkey', 'refresh_tokens', 'users', ['user_id'], ['id'])
