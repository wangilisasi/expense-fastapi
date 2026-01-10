"""
Tests for authentication functionality.

These tests are CRITICAL - authentication is your security boundary.
If these break, your app's security is compromised.
"""
import pytest
from datetime import timedelta
from jose import jwt

from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_user_by_username,
    SECRET_KEY,
    ALGORITHM,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hash_is_different_from_plain(self):
        """Hashed password should not equal plain password."""
        plain = "mysecretpassword"
        hashed = get_password_hash(plain)
        assert hashed != plain

    def test_verify_correct_password(self):
        """Correct password should verify successfully."""
        plain = "mysecretpassword"
        hashed = get_password_hash(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password(self):
        """Wrong password should fail verification."""
        hashed = get_password_hash("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_different_hashes(self):
        """Same password should produce different hashes (due to salt)."""
        plain = "mysecretpassword"
        hash1 = get_password_hash(plain)
        hash2 = get_password_hash(plain)
        assert hash1 != hash2  # Different salts
        # But both should verify
        assert verify_password(plain, hash1) is True
        assert verify_password(plain, hash2) is True


class TestJWTToken:
    """Test JWT token creation and validation."""

    def test_create_token_contains_subject(self):
        """Token should contain the subject (username)."""
        token = create_access_token(data={"sub": "testuser"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"

    def test_create_token_has_expiration(self):
        """Token should have an expiration time."""
        token = create_access_token(data={"sub": "testuser"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_create_token_custom_expiration(self):
        """Token should respect custom expiration delta."""
        token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(minutes=5)
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_invalid_token_raises_error(self):
        """Invalid token should raise JWTError."""
        from jose import JWTError
        with pytest.raises(JWTError):
            jwt.decode("invalid.token.here", SECRET_KEY, algorithms=[ALGORITHM])


class TestUserAuthentication:
    """Test user authentication flow."""

    def test_get_user_by_username_exists(self, db, test_user):
        """Should return user when username exists."""
        user = get_user_by_username(db, "testuser")
        assert user is not None
        assert user.username == "testuser"

    def test_get_user_by_username_not_exists(self, db):
        """Should return None when username doesn't exist."""
        user = get_user_by_username(db, "nonexistent")
        assert user is None

    def test_authenticate_user_success(self, db, test_user):
        """Should return user with correct credentials."""
        user = authenticate_user(db, "testuser", "testpassword123")
        assert user is not None
        assert user.username == "testuser"

    def test_authenticate_user_wrong_password(self, db, test_user):
        """Should return None with wrong password."""
        user = authenticate_user(db, "testuser", "wrongpassword")
        assert user is None

    def test_authenticate_user_nonexistent_user(self, db):
        """Should return None for nonexistent user."""
        user = authenticate_user(db, "nonexistent", "anypassword")
        assert user is None


class TestAuthEndpoints:
    """Test authentication API endpoints."""

    def test_register_success(self, client):
        """Should create a new user successfully."""
        response = client.post("/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "uuid_id" in data
        # Password should NOT be in response
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client, test_user):
        """Should reject duplicate username."""
        response = client.post("/register", json={
            "username": "testuser",  # Already exists
            "email": "different@example.com",
            "password": "password123"
        })
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_duplicate_email(self, client, test_user):
        """Should reject duplicate email."""
        response = client.post("/register", json={
            "username": "differentuser",
            "email": "testuser@example.com",  # Already exists
            "password": "password123"
        })
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """Should return access token on successful login."""
        response = client.post("/login", data={
            "username": "testuser",
            "password": "testpassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Should reject wrong password."""
        response = client.post("/login", data={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Should reject nonexistent user."""
        response = client.post("/login", data={
            "username": "nonexistent",
            "password": "anypassword"
        })
        assert response.status_code == 401

    def test_get_me_authenticated(self, client, test_user, auth_headers):
        """Should return current user info when authenticated."""
        response = client.get("/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"

    def test_get_me_unauthenticated(self, client):
        """Should reject request without token."""
        response = client.get("/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """Should reject invalid token."""
        response = client.get("/me", headers={
            "Authorization": "Bearer invalid.token.here"
        })
        assert response.status_code == 401

    def test_get_me_expired_token(self, client, test_user):
        """Should reject expired token."""
        # Create a token that expired 1 hour ago
        expired_token = create_access_token(
            data={"sub": test_user.username},
            expires_delta=timedelta(hours=-1)
        )
        response = client.get("/me", headers={
            "Authorization": f"Bearer {expired_token}"
        })
        assert response.status_code == 401

