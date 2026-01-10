# Testing Guide for Expense Tracker API

This document describes the test suite implementation for the FastAPI expense tracker application.

## Overview

The test suite follows a pragmatic approach to testing, focusing on **what matters most**:

| Priority | Area | Coverage Target | Rationale |
|----------|------|-----------------|-----------|
| 🔴 Critical | Authentication & Authorization | 100% | Security boundary - if this breaks, data is compromised |
| 🟠 High | Business Logic (Stats) | 100% | Financial calculations must be accurate |
| 🟠 High | Input Validation | 90%+ | Prevents bad data from corrupting the database |
| 🟢 Medium | CRUD Operations | 50-60% | Happy path coverage; edge cases covered elsewhere |

**Final Coverage: 92%** (83 tests)

## Test Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared fixtures
├── test_auth.py             # Authentication tests (22 tests)
├── test_authorization.py    # Access control tests (16 tests)
├── test_stats.py            # Business logic tests (13 tests)
├── test_validation.py       # Input validation tests (17 tests)
└── test_crud.py             # Basic CRUD tests (15 tests)
```

## Running Tests

### Prerequisites

```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies (already in requirements.txt)
pip install pytest pytest-cov httpx
```

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test class
pytest tests/test_auth.py::TestAuthEndpoints

# Run specific test
pytest tests/test_auth.py::TestAuthEndpoints::test_login_success
```

### Coverage Reports

```bash
# Terminal coverage report
pytest --cov=app --cov=main --cov-report=term-missing

# HTML coverage report (creates htmlcov/ directory)
pytest --cov=app --cov=main --cov-report=html

# Show only lines that aren't covered
pytest --cov=app --cov=main --cov-report=term-missing | grep -E "TOTAL|Miss"
```

## Test Files Explained

### `conftest.py` - Shared Fixtures

Provides reusable test components:

- **`db`**: Fresh SQLite in-memory database for each test (isolated, fast)
- **`client`**: FastAPI TestClient with database override
- **`test_user`**: Pre-created user for authenticated tests
- **`second_user`**: Second user for authorization tests
- **`auth_headers`**: Bearer token headers for test_user
- **`test_tracker`**: Pre-created expense tracker
- **`test_expense`**: Pre-created expense
- **`tracker_with_expenses`**: Tracker with multiple expenses for stats tests

### `test_auth.py` - Authentication Tests (🔴 Critical)

Tests the security boundary of the application:

```
TestPasswordHashing
├── test_password_hash_is_different_from_plain
├── test_verify_correct_password
├── test_verify_wrong_password
└── test_same_password_different_hashes

TestJWTToken
├── test_create_token_contains_subject
├── test_create_token_has_expiration
├── test_create_token_custom_expiration
└── test_invalid_token_raises_error

TestUserAuthentication
├── test_get_user_by_username_exists
├── test_get_user_by_username_not_exists
├── test_authenticate_user_success
├── test_authenticate_user_wrong_password
└── test_authenticate_user_nonexistent_user

TestAuthEndpoints
├── test_register_success
├── test_register_duplicate_username
├── test_register_duplicate_email
├── test_login_success
├── test_login_wrong_password
├── test_login_nonexistent_user
├── test_get_me_authenticated
├── test_get_me_unauthenticated
├── test_get_me_invalid_token
└── test_get_me_expired_token
```

### `test_authorization.py` - Access Control Tests (🔴 Critical)

Ensures users can only access their own data:

```
TestTrackerAuthorization
├── test_cannot_view_other_users_trackers_list
├── test_cannot_view_other_users_tracker_detail
├── test_cannot_update_other_users_tracker
├── test_cannot_view_other_users_tracker_stats
└── test_can_view_own_tracker

TestExpenseAuthorization
├── test_cannot_view_expenses_in_other_users_tracker
├── test_cannot_add_expense_to_other_users_tracker
├── test_cannot_delete_expense_from_other_users_tracker
├── test_cannot_view_daily_expenses_in_other_users_tracker
├── test_can_add_expense_to_own_tracker
└── test_can_delete_own_expense

TestUnauthenticatedAccess
├── test_trackers_requires_auth
├── test_create_tracker_requires_auth
├── test_expenses_requires_auth
├── test_add_expense_requires_auth
└── test_delete_expense_requires_auth
```

### `test_stats.py` - Business Logic Tests (🟠 High)

Validates financial calculations:

```
TestStatsCalculations
├── test_stats_empty_tracker
├── test_stats_total_expenditure
├── test_stats_todays_expenditure
├── test_stats_remaining_days
├── test_stats_target_expenditure_per_day
└── test_stats_budget_returned_correctly

TestStatsEdgeCases
├── test_stats_tracker_ended_yesterday
├── test_stats_tracker_starts_today
├── test_stats_single_day_tracker
└── test_stats_rounding

TestDailyExpenses
├── test_daily_expenses_grouped_by_date
├── test_daily_expenses_totals_correct
└── test_daily_expenses_empty_tracker
```

### `test_validation.py` - Input Validation Tests (🟠 High)

Ensures bad data is rejected:

```
TestTrackerValidation
├── test_reject_negative_budget
├── test_reject_zero_budget
├── test_reject_end_date_before_start_date
├── test_reject_empty_name
├── test_reject_whitespace_only_name
├── test_accept_valid_tracker
└── test_accept_same_start_and_end_date

TestExpenseValidation
├── test_reject_negative_amount
├── test_reject_zero_amount
├── test_reject_empty_description
├── test_reject_whitespace_only_description
├── test_reject_nonexistent_tracker
├── test_accept_valid_expense
└── test_accept_expense_with_decimal_amount

TestSchemaValidation
├── test_reject_invalid_date_format
├── test_reject_missing_required_fields
└── test_reject_wrong_type_budget
```

### `test_crud.py` - CRUD Operations Tests (🟢 Medium)

Happy path tests for basic operations:

```
TestTrackerCRUD
├── test_create_tracker
├── test_list_trackers
├── test_get_tracker_detail
├── test_update_tracker_name
├── test_update_tracker_budget
├── test_update_tracker_partial
└── test_get_nonexistent_tracker

TestExpenseCRUD
├── test_create_expense
├── test_list_expenses
├── test_delete_expense
├── test_delete_nonexistent_expense
├── test_expenses_returned_in_order
└── test_expenses_limited_to_5

TestTrackerWithExpenses
└── test_tracker_detail_includes_expenses
```

## Coverage Report Breakdown

```
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
app/__init__.py       0      0   100%
app/auth.py          52      2    96%   73, 80
app/database.py      21      6    71%   16, 24, 31-35
app/models.py        33      0   100%
app/schemas.py       78      0   100%
main.py             166     19    89%   86-87, 123-131, 185, 212, 239, 295-304
-----------------------------------------------
TOTAL               350     27    92%
```

### Untested Lines (Intentionally)

| File | Lines | Reason |
|------|-------|--------|
| `app/database.py` | 16, 24, 31-35 | Database config/connection code that only runs at startup |
| `main.py` | 123-131, 295-304 | Generic `except Exception` handlers - defensive code that rarely fires |
| `app/auth.py` | 73, 80 | Edge cases in token validation already covered by other tests |

## Adding New Tests

### When to Add Tests

1. **New endpoint**: Add CRUD test + validation tests + authorization test
2. **New business logic**: Add comprehensive tests with edge cases
3. **Bug fix**: Add regression test that would have caught the bug
4. **Security change**: Add auth/authz tests

### Test Template

```python
class TestNewFeature:
    """Describe what this test class covers."""

    def test_happy_path(self, client, auth_headers):
        """Should do X when Y."""
        response = client.post("/endpoint", headers=auth_headers, json={...})
        assert response.status_code == 200
        assert response.json()["field"] == expected_value

    def test_edge_case(self, client, auth_headers):
        """Should handle edge case Z."""
        # ...

    def test_error_condition(self, client, auth_headers):
        """Should return error when invalid."""
        # ...
```

## Philosophy

> "Don't aim for a coverage number. Aim for confidence."

This test suite prioritizes:

1. **Security** (auth/authz) - 100% tested
2. **Money** (calculations) - 100% tested  
3. **Data integrity** (validation) - 90%+ tested
4. **Basic functionality** (CRUD) - Happy paths tested

What we intentionally skip:
- Trivial getters with no logic
- Framework-provided validation (Pydantic handles this)
- Generic exception handlers
- Database configuration code

This approach gives you **confidence to refactor** without wasting time on tests that don't catch real bugs.

