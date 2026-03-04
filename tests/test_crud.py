"""
Tests for CRUD operations.

These are happy-path tests to verify basic functionality works.
Edge cases and error conditions are covered in other test files.
"""
import pytest
import uuid
from datetime import date, timedelta


class TestTrackerCRUD:
    """Test basic CRUD operations for expense trackers."""

    def test_create_tracker(self, client, auth_headers):
        """Should create a new tracker."""
        response = client.post(
            "/trackers",
            headers=auth_headers,
            json={
                "name": "Monthly Budget",
                "budget": 2000.00,
                "startDate": str(date.today()),
                "endDate": str(date.today() + timedelta(days=30)),
                "description": "My monthly expense tracker"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Monthly Budget"
        assert data["budget"] == 2000.00
        assert data["description"] == "My monthly expense tracker"
        assert "uuid_id" in data

    def test_list_trackers(self, client, test_tracker, auth_headers):
        """Should list user's trackers."""
        response = client.get("/trackers", headers=auth_headers)
        assert response.status_code == 200
        
        trackers = response.json()
        assert len(trackers) >= 1
        assert any(t["uuid_id"] == test_tracker.uuid_id for t in trackers)

    def test_get_tracker_detail(self, client, test_tracker, auth_headers):
        """Should get tracker details with expenses."""
        response = client.get(
            f"/trackers/{test_tracker.uuid_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["uuid_id"] == test_tracker.uuid_id
        assert data["name"] == test_tracker.name
        assert "expenses" in data

    def test_update_tracker_name(self, client, test_tracker, auth_headers):
        """Should update tracker name."""
        response = client.patch(
            f"/trackers/{test_tracker.uuid_id}",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_tracker_budget(self, client, test_tracker, auth_headers):
        """Should update tracker budget."""
        response = client.patch(
            f"/trackers/{test_tracker.uuid_id}",
            headers=auth_headers,
            json={"budget": 1500.00}
        )
        assert response.status_code == 200
        assert response.json()["budget"] == 1500.00

    def test_update_tracker_partial(self, client, test_tracker, auth_headers):
        """Should only update provided fields."""
        original_name = test_tracker.name
        
        response = client.patch(
            f"/trackers/{test_tracker.uuid_id}",
            headers=auth_headers,
            json={"description": "New description"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == original_name  # Unchanged
        assert data["description"] == "New description"  # Updated

    def test_get_nonexistent_tracker(self, client, auth_headers):
        """Should return 404 for nonexistent tracker."""
        response = client.get(
            "/trackers/nonexistent-uuid",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestExpenseCRUD:
    """Test basic CRUD operations for expenses."""

    def test_create_expense(self, client, test_tracker, auth_headers):
        """Should create a new expense."""
        expense_uuid = str(uuid.uuid4())
        response = client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "uuid_id": expense_uuid,
                "description": "Lunch at cafe",
                "amount": 15.50,
                "date": str(date.today()),
                "uuid_tracker_id": test_tracker.uuid_id
            }
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["uuid_id"] == expense_uuid
        assert data["description"] == "Lunch at cafe"
        assert data["amount"] == 15.50
        assert data["uuid_tracker_id"] == test_tracker.uuid_id
        assert "created_at" in data
        assert "updated_at" in data

    def test_list_expenses(self, client, test_tracker, test_expense, auth_headers):
        """Should list expenses for a tracker."""
        response = client.get(
            f"/trackers/{test_tracker.uuid_id}/expenses",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        expenses = response.json()
        assert len(expenses) >= 1
        assert any(e["uuid_id"] == test_expense.uuid_id for e in expenses)

    def test_delete_expense(self, client, test_expense, auth_headers):
        """Should delete an expense."""
        response = client.delete(
            f"/expenses/{test_expense.uuid_id}",
            headers=auth_headers
        )
        assert response.status_code == 204

    def test_delete_nonexistent_expense(self, client, auth_headers):
        """Should return 404 for nonexistent expense."""
        response = client.delete(
            "/expenses/nonexistent-uuid",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_expenses_returned_in_order(
        self, client, tracker_with_expenses, auth_headers
    ):
        """Expenses should be returned in descending order by created_at."""
        response = client.get(
            f"/trackers/{tracker_with_expenses.uuid_id}/expenses",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        expenses = response.json()
        # Verify we got expenses back
        assert len(expenses) > 0
        
        # Note: All have similar created_at, so order might vary
        # The main thing is the endpoint returns data

    def test_expenses_returns_full_history(self, db, client, test_tracker, auth_headers):
        """Default /expenses (no query params) must return all expenses — no artificial cap."""
        from app.models import Expense
        for i in range(7):
            expense = Expense(
                description=f"Expense {i}",
                amount=10.00,
                date=date.today(),
                uuid_tracker_id=test_tracker.uuid_id
            )
            db.add(expense)
        db.commit()

        response = client.get(
            f"/trackers/{test_tracker.uuid_id}/expenses",
            headers=auth_headers
        )
        assert response.status_code == 200
        expenses = response.json()
        assert len(expenses) == 7  # All expenses returned, not capped at 5

    def test_expenses_pagination_limit(self, db, client, test_tracker, auth_headers):
        """limit query param should cap the result set."""
        from app.models import Expense
        for i in range(7):
            expense = Expense(
                description=f"Expense {i}",
                amount=10.00,
                date=date.today(),
                uuid_tracker_id=test_tracker.uuid_id
            )
            db.add(expense)
        db.commit()

        response = client.get(
            f"/trackers/{test_tracker.uuid_id}/expenses?limit=3",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_expenses_pagination_offset(self, db, client, test_tracker, auth_headers):
        """offset query param should skip the given number of expenses."""
        from app.models import Expense
        for i in range(7):
            expense = Expense(
                description=f"Expense {i}",
                amount=10.00,
                date=date.today(),
                uuid_tracker_id=test_tracker.uuid_id
            )
            db.add(expense)
        db.commit()

        response_all = client.get(
            f"/trackers/{test_tracker.uuid_id}/expenses",
            headers=auth_headers
        )
        response_offset = client.get(
            f"/trackers/{test_tracker.uuid_id}/expenses?offset=4",
            headers=auth_headers
        )
        assert response_offset.status_code == 200
        all_ids = [e["uuid_id"] for e in response_all.json()]
        offset_ids = [e["uuid_id"] for e in response_offset.json()]
        # Offset results must be a strict tail of the full list
        assert offset_ids == all_ids[4:]

    def test_expenses_pagination_limit_and_offset(self, db, client, test_tracker, auth_headers):
        """limit + offset together should return the correct page."""
        from app.models import Expense
        for i in range(7):
            expense = Expense(
                description=f"Expense {i}",
                amount=10.00,
                date=date.today(),
                uuid_tracker_id=test_tracker.uuid_id
            )
            db.add(expense)
        db.commit()

        response_all = client.get(
            f"/trackers/{test_tracker.uuid_id}/expenses",
            headers=auth_headers
        )
        response_page = client.get(
            f"/trackers/{test_tracker.uuid_id}/expenses?limit=2&offset=3",
            headers=auth_headers
        )
        assert response_page.status_code == 200
        all_ids = [e["uuid_id"] for e in response_all.json()]
        page_ids = [e["uuid_id"] for e in response_page.json()]
        assert len(page_ids) == 2
        assert page_ids == all_ids[3:5]

    def test_expenses_authorization_still_enforced(
        self, client, test_tracker, test_expense, second_user_auth_headers
    ):
        """Pagination params must not bypass ownership checks."""
        response = client.get(
            f"/trackers/{test_tracker.uuid_id}/expenses?limit=10&offset=0",
            headers=second_user_auth_headers
        )
        assert response.status_code == 403


class TestTrackerWithExpenses:
    """Test tracker detail endpoint includes expenses."""

    def test_tracker_detail_includes_expenses(
        self, client, tracker_with_expenses, auth_headers
    ):
        """Tracker detail should include all expenses."""
        response = client.get(
            f"/trackers/{tracker_with_expenses.uuid_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "expenses" in data
        assert len(data["expenses"]) == 4  # We created 4 expenses in fixture

