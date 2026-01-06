"""
Tests for authentication module
"""
import pytest
from httpx import AsyncClient

from auth import (
    verify_password,
    create_session_token,
    verify_session_token,
    can_modify_booking,
    User
)


class TestVerifyPassword:
    """Tests for password verification"""

    def test_valid_admin_login(self):
        """Admin can login with correct password"""
        user = verify_password("Admin", "admin123")
        assert user is not None
        assert user.is_admin is True
        assert user.party_id is None
        assert user.username == "Admin"

    def test_valid_party_login(self):
        """Party user can login with correct password"""
        user = verify_password("Siggi & Mausi", "test1")
        assert user is not None
        assert user.is_admin is False
        assert user.party_id == 1
        assert user.username == "Siggi & Mausi"

    def test_invalid_password(self):
        """Wrong password returns None"""
        user = verify_password("Admin", "wrongpassword")
        assert user is None

    def test_invalid_username(self):
        """Unknown username returns None"""
        user = verify_password("Unknown", "anypassword")
        assert user is None

    def test_empty_password(self):
        """Empty password returns None"""
        user = verify_password("Admin", "")
        assert user is None


class TestSessionToken:
    """Tests for JWT token creation and verification"""

    def test_create_and_verify_token(self):
        """Token can be created and verified"""
        user = User(party_id=1, is_admin=False, username="Test")
        token = create_session_token(user)

        verified_user = verify_session_token(token)
        assert verified_user is not None
        assert verified_user.party_id == 1
        assert verified_user.is_admin is False
        assert verified_user.username == "Test"

    def test_admin_token(self):
        """Admin token contains correct info"""
        user = User(party_id=None, is_admin=True, username="Admin")
        token = create_session_token(user)

        verified_user = verify_session_token(token)
        assert verified_user is not None
        assert verified_user.is_admin is True
        assert verified_user.party_id is None

    def test_invalid_token(self):
        """Invalid token returns None"""
        result = verify_session_token("invalid-token")
        assert result is None

    def test_tampered_token(self):
        """Tampered token returns None"""
        user = User(party_id=1, is_admin=False, username="Test")
        token = create_session_token(user)
        tampered = token[:-5] + "xxxxx"

        result = verify_session_token(tampered)
        assert result is None


class TestCanModifyBooking:
    """Tests for booking modification permissions"""

    def test_admin_can_modify_any(self):
        """Admin can modify any party's booking"""
        admin = User(party_id=None, is_admin=True, username="Admin")
        assert can_modify_booking(admin, 1) is True
        assert can_modify_booking(admin, 2) is True
        assert can_modify_booking(admin, 3) is True

    def test_user_can_modify_own(self):
        """User can modify their own party's booking"""
        user = User(party_id=1, is_admin=False, username="Siggi & Mausi")
        assert can_modify_booking(user, 1) is True

    def test_user_cannot_modify_other(self):
        """User cannot modify other party's booking"""
        user = User(party_id=1, is_admin=False, username="Siggi & Mausi")
        assert can_modify_booking(user, 2) is False
        assert can_modify_booking(user, 3) is False


class TestLoginEndpoint:
    """Tests for login API endpoint"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Successful login returns token"""
        response = await client.post("/api/auth/login", json={
            "username": "Admin",
            "password": "admin123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["is_admin"] is True

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Wrong password returns 401"""
        response = await client.post("/api/auth/login", json={
            "username": "Admin",
            "password": "wrongpassword"
        })

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_unknown_user(self, client: AsyncClient):
        """Unknown user returns 401"""
        response = await client.post("/api/auth/login", json={
            "username": "Unknown",
            "password": "anypassword"
        })

        assert response.status_code == 401


class TestMeEndpoint:
    """Tests for /me endpoint"""

    @pytest.mark.asyncio
    async def test_me_authenticated(self, client: AsyncClient, auth_headers_admin: dict):
        """Authenticated user can get their info"""
        response = await client.get("/api/auth/me", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is True
        assert data["username"] == "Admin"

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, client: AsyncClient):
        """Unauthenticated request returns 401"""
        response = await client.get("/api/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_invalid_token(self, client: AsyncClient):
        """Invalid token returns 401"""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
