# Alembic Migration Setup Documentation

## Overview

This document describes the implementation of database migrations using Alembic for the FastAPI expense tracking application. The migration system was set up to handle the addition of user authentication and the associated database schema changes.

## Why Alembic?

Alembic is the database migration tool for SQLAlchemy. It provides:
- Version control for database schema changes
- Safe, reversible migrations
- Support for complex schema modifications
- Integration with SQLAlchemy models
- Environment-specific configuration

## Setup Process

### 1. Added Alembic Dependency

Added `alembic==1.14.0` to `requirements.txt` to include the migration tool.

### 2. Initialized Alembic Configuration

```bash
alembic init alembic
```

This created:
- `alembic.ini` - Main configuration file
- `alembic/` directory - Contains migration scripts and environment configuration
- `alembic/env.py` - Environment configuration for connecting to database
- `alembic/versions/` - Directory for migration files

### 3. Configured Environment

Modified `alembic/env.py` to:
- Import our database configuration and models
- Set `target_metadata = Base.metadata` for autogenerate support
- Configure database URL from environment variables
- Handle Railway's PostgreSQL URL format conversion

Key changes to `alembic/env.py`:
```python
from app.database import Base
from app.models import User, ExpenseTracker, Expense
target_metadata = Base.metadata

# Set database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

### 4. Updated Configuration File

Modified `alembic.ini` to remove hardcoded database URL and rely on environment variables instead.

## Migration Files Created

### 1. Initial Migration (90185bbb703e)
**File**: `90185bbb703e_add_user_authentication_and_.py`
**Purpose**: Add user authentication and relationships to existing database

This migration:
- Creates the `users` table with authentication fields
- Adds indexes for username and email uniqueness
- Adds `user_id` column to `expensetracker` table
- Handles existing data by creating a default user
- Establishes foreign key relationships

### 2. User ID Addition (3fa6dc0f5645)
**File**: `3fa6dc0f5645_add_user_id_to_expensetracker.py`
**Purpose**: Add user_id column to expensetracker table with proper data handling

This migration:
- Adds `user_id` column as nullable initially
- Checks for existing expense trackers
- Creates/uses a default user for existing data
- Updates existing records with the default user ID
- Makes the column non-nullable
- Adds foreign key constraint

## Database Schema Changes

### New Tables Added:
- **users**: Stores user authentication information
  - `id` (Primary Key)
  - `username` (Unique)
  - `email` (Unique)
  - `hashed_password`

### Modified Tables:
- **expensetracker**: Added user ownership
  - `user_id` (Foreign Key to users.id)

### Relationships Established:
- User → ExpenseTracker (One-to-Many)
- ExpenseTracker → Expense (One-to-Many) [existing]

## Handling Existing Data

The migration process carefully handles existing data:

1. **Existing Tables**: The database already contained `users`, `expensetracker`, and `expense` tables
2. **Data Preservation**: All existing expense trackers and expenses were preserved
3. **Default User**: A default user was created for existing expense trackers:
   - Username: `default_user`
   - Email: `default@example.com`
   - Password: Default hashed password (should be changed in production)

## Migration Commands Used

```bash
# Install Alembic
pip install alembic==1.14.0

# Initialize Alembic
alembic init alembic

# Mark existing schema as current (database already had tables)
alembic stamp head

# Create migration for user_id addition
alembic revision -m "Add user_id to expensetracker"

# Apply migrations
alembic upgrade head

# Check current migration state
alembic current

# Generate automatic migration (for verification)
alembic revision --autogenerate -m "description"
```

## Current Migration State

The database is now fully synchronized with the SQLAlchemy models. The migration history shows:
1. `90185bbb703e` - Initial user authentication setup
2. `3fa6dc0f5645` - User ID addition to expense trackers

## Future Migrations

To create new migrations:

1. **Modify models** in `app/models.py`
2. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
3. **Review generated migration** in `alembic/versions/`
4. **Apply migration**:
   ```bash
   alembic upgrade head
   ```

## Best Practices Implemented

1. **Safe Column Addition**: Added NOT NULL columns by first making them nullable, populating data, then making them non-nullable
2. **Data Integrity**: Ensured existing data is preserved and properly linked
3. **Reversible Migrations**: All migrations include proper downgrade functions
4. **Environment Configuration**: Used environment variables for database configuration
5. **Model Synchronization**: Ensured models are imported in `env.py` for autogenerate support

## Troubleshooting

### Common Issues and Solutions:

1. **"Target database is not up to date"**
   - Use `alembic stamp head` to mark current state
   - This happens when adding migrations to existing database

2. **"Column cannot be null" errors**
   - Add columns as nullable first, populate data, then make non-nullable
   - Handle existing data appropriately

3. **"Table already exists"**
   - Use `alembic stamp head` to sync migration state
   - Or create migration that checks if table exists before creating

## Security Considerations

- Default user created for existing data should have password changed
- Environment variables protect database credentials
- Migration scripts should be reviewed before applying to production

## Conclusion

The Alembic migration system is now successfully set up and functional. The database schema has been updated to support user authentication while preserving all existing data. Future schema changes can be handled safely through the migration system. 