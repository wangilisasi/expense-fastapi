"""
Tests for input validation rules.

These tests verify that your validation logic rejects bad data
before it corrupts your database or causes calculation errors.
"""
import pytest
from datetime import date, timedelta


class TestTrackerValidation:
    """Test validation rules for expense trackers."""

    def test_reject_negative_budget(self, client, auth_headers):
        """Should reject budget less than or equal to 0."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "Test Tracker",
                "budget": -100,
                "startDate": str(date.today()),
                "endDate": str(date.today() + timedelta(days=30))
            }
        )
        assert response.status_code == 400
        assert "Budget must be greater than 0" in response.json()["detail"]

    def test_reject_zero_budget(self, client, auth_headers):
        """Should reject zero budget."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "Test Tracker",
                "budget": 0,
                "startDate": str(date.today()),
                "endDate": str(date.today() + timedelta(days=30))
            }
        )
        assert response.status_code == 400
        assert "Budget must be greater than 0" in response.json()["detail"]

    def test_reject_end_date_before_start_date(self, client, auth_headers):
        """Should reject when end date is before start date."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "Test Tracker",
                "budget": 1000,
                "startDate": str(date.today() + timedelta(days=10)),
                "endDate": str(date.today())  # Before start
            }
        )
        assert response.status_code == 400
        assert "Start date cannot be after end date" in response.json()["detail"]

    def test_reject_empty_name(self, client, auth_headers):
        """Should reject empty tracker name."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "",
                "budget": 1000,
                "startDate": str(date.today()),
                "endDate": str(date.today() + timedelta(days=30))
            }
        )
        assert response.status_code == 400
        assert "Tracker name cannot be empty" in response.json()["detail"]

    def test_reject_whitespace_only_name(self, client, auth_headers):
        """Should reject tracker name that's only whitespace."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "   ",
                "budget": 1000,
                "startDate": str(date.today()),
                "endDate": str(date.today() + timedelta(days=30))
            }
        )
        assert response.status_code == 400
        assert "Tracker name cannot be empty" in response.json()["detail"]

    def test_accept_valid_tracker(self, client, auth_headers):
        """Should accept valid tracker data."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "Valid Tracker",
                "budget": 1000,
                "startDate": str(date.today()),
                "endDate": str(date.today() + timedelta(days=30)),
                "description": "A valid description"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Valid Tracker"
        assert data["budget"] == 1000

    def test_accept_same_start_and_end_date(self, client, auth_headers):
        """Should accept tracker where start and end are the same day."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "Single Day Budget",
                "budget": 100,
                "startDate": str(date.today()),
                "endDate": str(date.today())  # Same day is valid
            }
        )
        assert response.status_code == 200


class TestExpenseValidation:
    """Test validation rules for expenses."""

    def test_reject_negative_amount(self, client, test_tracker, auth_headers):
        """Should reject negative expense amount."""
        response = client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "description": "Test expense",
                "amount": -50,
                "date": str(date.today()),
                "uuid_tracker_id": test_tracker.uuid_id
            }
        )
        assert response.status_code == 400
        assert "amount must be greater than 0" in response.json()["detail"]

    def test_reject_zero_amount(self, client, test_tracker, auth_headers):
        """Should reject zero expense amount."""
        response = client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "description": "Test expense",
                "amount": 0,
                "date": str(date.today()),
                "uuid_tracker_id": test_tracker.uuid_id
            }
        )
        assert response.status_code == 400
        assert "amount must be greater than 0" in response.json()["detail"]

    def test_reject_empty_description(self, client, test_tracker, auth_headers):
        """Should reject empty expense description."""
        response = client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "description": "",
                "amount": 50,
                "date": str(date.today()),
                "uuid_tracker_id": test_tracker.uuid_id
            }
        )
        assert response.status_code == 400
        assert "description cannot be empty" in response.json()["detail"]

    def test_reject_whitespace_only_description(
        self, client, test_tracker, auth_headers
    ):
        """Should reject description that's only whitespace."""
        response = client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "description": "   ",
                "amount": 50,
                "date": str(date.today()),
                "uuid_tracker_id": test_tracker.uuid_id
            }
        )
        assert response.status_code == 400
        assert "description cannot be empty" in response.json()["detail"]

    def test_reject_nonexistent_tracker(self, client, auth_headers):
        """Should reject expense for nonexistent tracker."""
        response = client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "description": "Test expense",
                "amount": 50,
                "date": str(date.today()),
                "uuid_tracker_id": "nonexistent-uuid-here"
            }
        )
        assert response.status_code == 404
        assert "Tracker not found" in response.json()["detail"]

    def test_accept_valid_expense(self, client, test_tracker, auth_headers):
        """Should accept valid expense data."""
        response = client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "description": "Coffee",
                "amount": 5.50,
                "date": str(date.today()),
                "uuid_tracker_id": test_tracker.uuid_id
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Coffee"
        assert data["amount"] == 5.50

    def test_accept_expense_with_decimal_amount(
        self, client, test_tracker, auth_headers
    ):
        """Should accept expense with decimal amount."""
        response = client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "description": "Precise expense",
                "amount": 123.45,
                "date": str(date.today()),
                "uuid_tracker_id": test_tracker.uuid_id
            }
        )
        assert response.status_code == 201
        assert response.json()["amount"] == 123.45


class TestSchemaValidation:
    """Test that Pydantic schemas reject invalid data."""

    def test_reject_invalid_date_format(self, client, auth_headers):
        """Should reject invalid date format."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "Test",
                "budget": 1000,
                "startDate": "not-a-date",
                "endDate": "2024-12-31"
            }
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_reject_missing_required_fields(self, client, auth_headers):
        """Should reject missing required fields."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "Test"
                # Missing budget, startDate, endDate
            }
        )
        assert response.status_code == 422

    def test_reject_wrong_type_budget(self, client, auth_headers):
        """Should reject non-numeric budget."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "Test",
                "budget": "not a number",
                "startDate": str(date.today()),
                "endDate": str(date.today() + timedelta(days=30))
            }
        )
        assert response.status_code == 422

