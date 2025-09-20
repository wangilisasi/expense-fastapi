"""Add UUID columns for migration to UUID primary keys

Revision ID: 449996f77b27
Revises: 3fa6dc0f5645
Create Date: 2025-09-20 09:31:58.328794

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '449996f77b27'
down_revision: Union[str, None] = '3fa6dc0f5645'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension for PostgreSQL (if using PostgreSQL)
    # For SQLite, we'll use string representation of UUIDs
    connection = op.get_bind()
    
    # Add UUID columns to all tables
    # Users table
    op.add_column('users', sa.Column('uuid_id', sa.String(36), nullable=True, unique=True))
    
    # ExpenseTracker table  
    op.add_column('expensetracker', sa.Column('uuid_id', sa.String(36), nullable=True, unique=True))
    op.add_column('expensetracker', sa.Column('uuid_user_id', sa.String(36), nullable=True))
    
    # Expense table
    op.add_column('expense', sa.Column('uuid_id', sa.String(36), nullable=True, unique=True))
    op.add_column('expense', sa.Column('uuid_tracker_id', sa.String(36), nullable=True))
    
    # Generate UUIDs for existing records
    # Users
    users_result = connection.execute(sa.text("SELECT id FROM users"))
    users = users_result.fetchall()
    user_uuid_mapping = {}
    
    for user in users:
        user_uuid = str(uuid.uuid4())
        user_uuid_mapping[user[0]] = user_uuid
        connection.execute(
            sa.text("UPDATE users SET uuid_id = :uuid_id WHERE id = :id"),
            {"uuid_id": user_uuid, "id": user[0]}
        )
    
    # ExpenseTracker
    trackers_result = connection.execute(sa.text("SELECT id, user_id FROM expensetracker"))
    trackers = trackers_result.fetchall()
    tracker_uuid_mapping = {}
    
    for tracker in trackers:
        tracker_uuid = str(uuid.uuid4())
        tracker_uuid_mapping[tracker[0]] = tracker_uuid
        user_uuid = user_uuid_mapping.get(tracker[1])
        connection.execute(
            sa.text("UPDATE expensetracker SET uuid_id = :uuid_id, uuid_user_id = :uuid_user_id WHERE id = :id"),
            {"uuid_id": tracker_uuid, "uuid_user_id": user_uuid, "id": tracker[0]}
        )
    
    # Expenses
    expenses_result = connection.execute(sa.text('SELECT id, "trackerId" FROM expense'))
    expenses = expenses_result.fetchall()
    
    for expense in expenses:
        expense_uuid = str(uuid.uuid4())
        tracker_uuid = tracker_uuid_mapping.get(expense[1])
        connection.execute(
            sa.text("UPDATE expense SET uuid_id = :uuid_id, uuid_tracker_id = :uuid_tracker_id WHERE id = :id"),
            {"uuid_id": expense_uuid, "uuid_tracker_id": tracker_uuid, "id": expense[0]}
        )
    
    # Make UUID columns non-nullable after populating them
    op.alter_column('users', 'uuid_id', nullable=False)
    op.alter_column('expensetracker', 'uuid_id', nullable=False)
    op.alter_column('expensetracker', 'uuid_user_id', nullable=False)
    op.alter_column('expense', 'uuid_id', nullable=False)
    op.alter_column('expense', 'uuid_tracker_id', nullable=False)
    
    # Add indexes for better performance
    op.create_index('ix_users_uuid_id', 'users', ['uuid_id'], unique=True)
    op.create_index('ix_expensetracker_uuid_id', 'expensetracker', ['uuid_id'], unique=True)
    op.create_index('ix_expensetracker_uuid_user_id', 'expensetracker', ['uuid_user_id'])
    op.create_index('ix_expense_uuid_id', 'expense', ['uuid_id'], unique=True)
    op.create_index('ix_expense_uuid_tracker_id', 'expense', ['uuid_tracker_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_expense_uuid_tracker_id', table_name='expense')
    op.drop_index('ix_expense_uuid_id', table_name='expense')
    op.drop_index('ix_expensetracker_uuid_user_id', table_name='expensetracker')
    op.drop_index('ix_expensetracker_uuid_id', table_name='expensetracker')
    op.drop_index('ix_users_uuid_id', table_name='users')
    
    # Drop UUID columns
    op.drop_column('expense', 'uuid_tracker_id')
    op.drop_column('expense', 'uuid_id')
    op.drop_column('expensetracker', 'uuid_user_id')
    op.drop_column('expensetracker', 'uuid_id')
    op.drop_column('users', 'uuid_id')
