"""Shared test fixtures for integration tests."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.db.base import Base
from backend.app.main import app
from backend.app.api.v1.dependencies import get_session

# Test database URL from environment or construct from main URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/snip_test",
)

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables before tests and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for each test."""
    async with test_async_session() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client for integration tests."""

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(client: AsyncClient) -> dict[str, Any]:
    """Create a test user and return user data with token."""
    import uuid

    # Generate unique email/username per test to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "testpassword123",
    }

    # Register user
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200

    token_data = login_response.json()
    return {
        **user_data,
        "access_token": token_data["access_token"],
        "id": response.json().get("id"),
    }


@pytest.fixture
def auth_headers(test_user: dict[str, Any]) -> dict[str, str]:
    """Provide authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {test_user['access_token']}"}


@pytest.fixture
async def another_user(client: AsyncClient) -> dict[str, Any]:
    """Create another test user for permission tests."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"another_{unique_id}@example.com",
        "username": f"anotheruser_{unique_id}",
        "password": "anotherpassword123",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200

    token_data = login_response.json()
    return {
        **user_data,
        "access_token": token_data["access_token"],
    }


@pytest.fixture
def another_auth_headers(another_user: dict[str, Any]) -> dict[str, str]:
    """Provide authorization headers for another user."""
    return {"Authorization": f"Bearer {another_user['access_token']}"}
