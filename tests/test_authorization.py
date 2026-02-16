"""
Tests for authorization - ensuring users can only access their own data.

These tests are CRITICAL. If authorization breaks, users can see/modify
other users' financial data. This would be a serious security incident.
"""
import pytest
import uuid
from datetime import date, timedelta


class TestTrackerAuthorization:
    """Test that users can only access their own trackers."""

    def test_cannot_view_other_users_trackers_list(
        self, client, test_user, second_user, test_tracker, second_user_auth_headers
    ):
        """User should not see trackers belonging to other users."""
        # test_tracker belongs to test_user, but we're logged in as second_user
        response = client.get("/trackers", headers=second_user_auth_headers)
        assert response.status_code == 200
        trackers = response.json()
        # second_user should see an empty list, not test_user's tracker
        assert len(trackers) == 0

    def test_cannot_view_other_users_tracker_detail(
        self, client, test_tracker, second_user_auth_headers
    ):
        """User should get 403 when trying to view another user's tracker."""
        response = client.get(
            f"/trackers/{test_tracker.uuid_id}",
            headers=second_user_auth_headers
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]

    def test_cannot_update_other_users_tracker(
        self, client, test_tracker, second_user_auth_headers
    ):
        """User should get 404 when trying to update another user's tracker."""
        response = client.patch(
            f"/trackers/{test_tracker.uuid_id}",
            headers=second_user_auth_headers,
            json={"name": "Hacked!"}
        )
        # Returns 404 because the query filters by user_id
        assert response.status_code == 404

    def test_cannot_view_other_users_tracker_stats(
        self, client, test_tracker, second_user_auth_headers
    ):
        """User should get 403 when trying to view another user's tracker stats."""
        response = client.get(
            f"/trackers/{test_tracker.uuid_id}/stats",
            headers=second_user_auth_headers
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]

    def test_can_view_own_tracker(self, client, test_tracker, auth_headers):
        """User should be able to view their own tracker."""
        response = client.get(
            f"/trackers/{test_tracker.uuid_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["uuid_id"] == test_tracker.uuid_id


class TestExpenseAuthorization:
    """Test that users can only access expenses in their own trackers."""

    def test_cannot_view_expenses_in_other_users_tracker(
        self, client, test_tracker, test_expense, second_user_auth_headers
    ):
        """User should get 403 when viewing expenses in another user's tracker."""
        response = client.get(
            f"/trackers/{test_tracker.uuid_id}/expenses",
            headers=second_user_auth_headers
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]

    def test_cannot_add_expense_to_other_users_tracker(
        self, client, test_tracker, second_user_auth_headers
    ):
        """User should get 403 when adding expense to another user's tracker."""
        response = client.post(
            "/expenses",
            headers=second_user_auth_headers,
            json={
                "uuid_id": str(uuid.uuid4()),
                "description": "Malicious expense",
                "amount": 999.99,
                "date": str(date.today()),
                "uuid_tracker_id": test_tracker.uuid_id
            }
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]

    def test_cannot_delete_expense_from_other_users_tracker(
        self, client, test_expense, second_user_auth_headers
    ):
        """User should get 403 when deleting expense from another user's tracker."""
        response = client.delete(
            f"/expenses/{test_expense.uuid_id}",
            headers=second_user_auth_headers
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]

    def test_cannot_view_daily_expenses_in_other_users_tracker(
        self, client, test_tracker, second_user_auth_headers
    ):
        """User should get 404 when viewing daily expenses in another user's tracker."""
        response = client.get(
            f"/trackers/{test_tracker.uuid_id}/daily-expenses",
            headers=second_user_auth_headers
        )
        assert response.status_code == 404

    def test_can_add_expense_to_own_tracker(
        self, client, test_tracker, auth_headers
    ):
        """User should be able to add expense to their own tracker."""
        response = client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "uuid_id": str(uuid.uuid4()),
                "description": "Legitimate expense",
                "amount": 25.00,
                "date": str(date.today()),
                "uuid_tracker_id": test_tracker.uuid_id
            }
        )
        assert response.status_code == 201

    def test_can_delete_own_expense(
        self, client, test_expense, auth_headers
    ):
        """User should be able to delete their own expense."""
        response = client.delete(
            f"/expenses/{test_expense.uuid_id}",
            headers=auth_headers
        )
        assert response.status_code == 204


class TestUnauthenticatedAccess:
    """Test that unauthenticated requests are rejected."""

    def test_trackers_requires_auth(self, client):
        """GET /trackers should require authentication."""
        response = client.get("/trackers")
        assert response.status_code == 401

    def test_create_tracker_requires_auth(self, client):
        """POST /trackers should require authentication."""
        response = client.post("/trackers", json={
            "name": "Test",
            "budget": 1000,
            "startDate": str(date.today()),
            "endDate": str(date.today() + timedelta(days=30))
        })
        assert response.status_code == 401

    def test_expenses_requires_auth(self, client, test_tracker):
        """GET /trackers/{id}/expenses should require authentication."""
        response = client.get(f"/trackers/{test_tracker.uuid_id}/expenses")
        assert response.status_code == 401

    def test_add_expense_requires_auth(self, client, test_tracker):
        """POST /expenses should require authentication."""
        response = client.post("/expenses", json={
            "uuid_id": str(uuid.uuid4()),
            "description": "Test",
            "amount": 10.00,
            "date": str(date.today()),
            "uuid_tracker_id": test_tracker.uuid_id
        })
        assert response.status_code == 401

    def test_delete_expense_requires_auth(self, client, test_expense):
        """DELETE /expenses/{id} should require authentication."""
        response = client.delete(f"/expenses/{test_expense.uuid_id}")
        assert response.status_code == 401

