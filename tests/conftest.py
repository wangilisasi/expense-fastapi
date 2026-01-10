"""
Pytest fixtures for testing the expense tracker API.

This module provides:
- In-memory SQLite database for fast, isolated tests
- TestClient with dependency overrides
- Pre-authenticated user fixtures
- Helper functions for creating test data
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import User, ExpenseTracker, Expense
from app.auth import get_password_hash, create_access_token
from main import app


# Use in-memory SQLite for tests (fast and isolated)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db) -> User:
    """Create a test user in the database."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def second_user(db) -> User:
    """Create a second test user for authorization tests."""
    user = User(
        username="seconduser",
        email="seconduser@example.com",
        hashed_password=get_password_hash("secondpassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> dict:
    """Create authorization headers for the test user."""
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_auth_headers(second_user) -> dict:
    """Create authorization headers for the second user."""
    token = create_access_token(data={"sub": second_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_tracker(db, test_user) -> ExpenseTracker:
    """Create a test expense tracker."""
    tracker = ExpenseTracker(
        name="Test Budget",
        description="A test expense tracker",
        budget=1000.00,
        startDate=date.today(),
        endDate=date.today() + timedelta(days=30),
        uuid_user_id=test_user.uuid_id
    )
    db.add(tracker)
    db.commit()
    db.refresh(tracker)
    return tracker


@pytest.fixture
def test_expense(db, test_tracker) -> Expense:
    """Create a test expense."""
    expense = Expense(
        description="Test expense",
        amount=50.00,
        date=date.today(),
        uuid_tracker_id=test_tracker.uuid_id
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@pytest.fixture
def tracker_with_expenses(db, test_tracker) -> ExpenseTracker:
    """Create a tracker with multiple expenses for stats testing."""
    today = date.today()
    expenses = [
        Expense(description="Coffee", amount=5.50, date=today, uuid_tracker_id=test_tracker.uuid_id),
        Expense(description="Lunch", amount=15.00, date=today, uuid_tracker_id=test_tracker.uuid_id),
        Expense(description="Groceries", amount=45.75, date=today - timedelta(days=1), uuid_tracker_id=test_tracker.uuid_id),
        Expense(description="Transport", amount=20.00, date=today - timedelta(days=2), uuid_tracker_id=test_tracker.uuid_id),
    ]
    for expense in expenses:
        db.add(expense)
    db.commit()
    db.refresh(test_tracker)
    return test_tracker

