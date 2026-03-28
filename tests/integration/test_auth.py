"""Integration tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    """Tests for POST /api/v1/auth/register."""

    async def test_register_success(self, client: AsyncClient):
        """Should register a new user successfully."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepassword123",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Should reject registration with existing email."""
        user_data = {
            "email": "duplicate@example.com",
            "username": "uniqueuser",
            "password": "password123",
        }

        # Register first time
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201

        # Try to register again with same email
        user_data["username"] = "differentuser"
        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    async def test_register_duplicate_username(self, client: AsyncClient):
        """Should reject registration with existing username."""
        user_data = {
            "email": "user1@example.com",
            "username": "duplicateusername",
            "password": "password123",
        }

        # Register first time
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201

        # Try to register again with same username
        user_data["email"] = "user2@example.com"
        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Should reject registration with invalid email."""
        user_data = {
            "email": "invalid-email",
            "username": "validuser",
            "password": "password123",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        """Should reject registration with missing fields."""
        # Missing password
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@test.com", "username": "test"},
        )
        assert response.status_code == 422

        # Missing email
        response = await client.post(
            "/api/v1/auth/register",
            json={"username": "test", "password": "password123"},
        )
        assert response.status_code == 422

        # Missing username
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@test.com", "password": "password123"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    async def test_login_success(self, client: AsyncClient):
        """Should login successfully with correct credentials."""
        # First register a user
        user_data = {
            "email": "logintest@example.com",
            "username": "logintest",
            "password": "testpassword123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        # Then login
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_email(self, client: AsyncClient):
        """Should reject login with non-existent email."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent@example.com", "password": "anypassword"},
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_login_invalid_password(self, client: AsyncClient):
        """Should reject login with wrong password."""
        # First register a user
        user_data = {
            "email": "wrongpass@example.com",
            "username": "wrongpass",
            "password": "correctpassword",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        # Try to login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_login_returns_valid_token(self, client: AsyncClient):
        """Token from login should be usable for authenticated requests."""
        # Register and login
        user_data = {
            "email": "tokentest@example.com",
            "username": "tokentest",
            "password": "password123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        token = login_response.json()["access_token"]

        # Use token to access protected endpoint
        response = await client.get(
            "/api/v1/links/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    async def test_login_case_sensitive_password(self, client: AsyncClient):
        """Password should be case sensitive."""
        user_data = {
            "email": "casesensitive@example.com",
            "username": "casesensitive",
            "password": "CaseSensitive123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        # Try lowercase password
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": "casesensitive123"},
        )
        assert response.status_code == 401

        # Correct case
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": "CaseSensitive123"},
        )
        assert response.status_code == 200
