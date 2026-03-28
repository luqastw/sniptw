"""Integration tests for link management endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCreateLink:
    """Tests for POST /api/v1/links/."""

    async def test_create_link_success(self, client: AsyncClient, auth_headers: dict):
        """Should create a new link successfully."""
        link_data = {"original_url": "https://example.com"}

        response = await client.post(
            "/api/v1/links/", json=link_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_url"] == "https://example.com/"
        assert "slug" in data
        assert "id" in data
        assert data["click_count"] == 0
        assert data["is_active"] is True

    async def test_create_link_with_custom_slug(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should create a link with custom slug."""
        link_data = {
            "original_url": "https://example.com/custom",
            "slug": "my-custom-slug",
        }

        response = await client.post(
            "/api/v1/links/", json=link_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "my-custom-slug"

    async def test_create_link_duplicate_slug(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should reject duplicate custom slug."""
        link_data = {
            "original_url": "https://example.com",
            "slug": "duplicate-slug-test",
        }

        # Create first link
        response = await client.post(
            "/api/v1/links/", json=link_data, headers=auth_headers
        )
        assert response.status_code == 200

        # Try to create second link with same slug
        link_data["original_url"] = "https://different.com"
        response = await client.post(
            "/api/v1/links/", json=link_data, headers=auth_headers
        )

        assert response.status_code == 409

    async def test_create_link_with_expiration(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should create a link with expiration."""
        link_data = {
            "original_url": "https://example.com",
            "expires_in_days": 7,
        }

        response = await client.post(
            "/api/v1/links/", json=link_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["expires_at"] is not None

    async def test_create_link_requires_auth(self, client: AsyncClient):
        """Should require authentication."""
        link_data = {"original_url": "https://example.com"}

        response = await client.post("/api/v1/links/", json=link_data)

        assert response.status_code == 401

    async def test_create_link_invalid_url(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should reject invalid URL."""
        link_data = {"original_url": "not-a-valid-url"}

        response = await client.post(
            "/api/v1/links/", json=link_data, headers=auth_headers
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestListLinks:
    """Tests for GET /api/v1/links/."""

    async def test_list_links_empty(self, client: AsyncClient):
        """Should return empty list for new user."""
        # Register a new user
        user_data = {
            "email": "emptylist@example.com",
            "username": "emptylist",
            "password": "password123",
        }
        await client.post("/api/v1/auth/register", json=user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/links/", headers=headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_list_links_returns_user_links(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should return only the user's links."""
        # Create a link
        link_data = {"original_url": "https://list-test.com"}
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        response = await client.get("/api/v1/links/", headers=auth_headers)

        assert response.status_code == 200
        links = response.json()
        assert len(links) >= 1
        assert any(link["original_url"] == "https://list-test.com/" for link in links)

    async def test_list_links_requires_auth(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.get("/api/v1/links/")

        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetLink:
    """Tests for GET /api/v1/links/{slug}."""

    async def test_get_link_success(self, client: AsyncClient, auth_headers: dict):
        """Should return link details."""
        # Create a link
        link_data = {"original_url": "https://get-test.com", "slug": "get-test-slug"}
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        response = await client.get("/api/v1/links/get-test-slug")

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "get-test-slug"
        assert data["original_url"] == "https://get-test.com/"

    async def test_get_link_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent link."""
        response = await client.get("/api/v1/links/nonexistent-slug")

        assert response.status_code == 404

    async def test_get_link_inactive_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should return 404 for inactive (deleted) link."""
        # Create and delete a link
        link_data = {"original_url": "https://example.com", "slug": "inactive-test"}
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)
        await client.delete("/api/v1/links/inactive-test", headers=auth_headers)

        response = await client.get("/api/v1/links/inactive-test")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestDeleteLink:
    """Tests for DELETE /api/v1/links/{slug}."""

    async def test_delete_link_success(self, client: AsyncClient, auth_headers: dict):
        """Should delete (soft delete) a link."""
        # Create a link
        link_data = {"original_url": "https://delete-test.com", "slug": "delete-me"}
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        response = await client.delete("/api/v1/links/delete-me", headers=auth_headers)

        assert response.status_code == 204

        # Verify link is no longer accessible
        get_response = await client.get("/api/v1/links/delete-me")
        assert get_response.status_code == 404

    async def test_delete_link_requires_auth(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.delete("/api/v1/links/some-slug")

        assert response.status_code == 401

    async def test_delete_link_not_found(self, client: AsyncClient, auth_headers: dict):
        """Should return 404 for non-existent link."""
        response = await client.delete(
            "/api/v1/links/nonexistent-slug", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_delete_link_forbidden_for_other_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        another_auth_headers: dict,
    ):
        """Should forbid deleting another user's link."""
        # Create link as first user
        link_data = {"original_url": "https://example.com", "slug": "owned-link"}
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        # Try to delete as second user
        response = await client.delete(
            "/api/v1/links/owned-link", headers=another_auth_headers
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestUpdateLink:
    """Tests for PATCH /api/v1/links/{slug}."""

    async def test_update_link_url(self, client: AsyncClient, auth_headers: dict):
        """Should update link URL."""
        # Create a link
        link_data = {"original_url": "https://original.com", "slug": "update-url-test"}
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        # Update the URL
        response = await client.patch(
            "/api/v1/links/update-url-test",
            json={"original_url": "https://updated.com"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_url"] == "https://updated.com"

    async def test_update_link_deactivate(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should deactivate a link."""
        # Create a link
        link_data = {
            "original_url": "https://example.com",
            "slug": "deactivate-test",
        }
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        # Deactivate
        response = await client.patch(
            "/api/v1/links/deactivate-test",
            json={"is_active": False},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    async def test_update_link_requires_auth(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.patch(
            "/api/v1/links/some-slug", json={"original_url": "https://example.com"}
        )

        assert response.status_code == 401

    async def test_update_link_forbidden_for_other_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        another_auth_headers: dict,
    ):
        """Should forbid updating another user's link."""
        # Create link as first user
        link_data = {"original_url": "https://example.com", "slug": "other-user-link"}
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        # Try to update as second user
        response = await client.patch(
            "/api/v1/links/other-user-link",
            json={"original_url": "https://hacked.com"},
            headers=another_auth_headers,
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestRedirect:
    """Tests for GET /{slug} (redirect endpoint)."""

    async def test_redirect_success(self, client: AsyncClient, auth_headers: dict):
        """Should redirect to original URL."""
        # Create a link
        link_data = {
            "original_url": "https://redirect-target.com",
            "slug": "redirect-test",
        }
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        response = await client.get("/redirect-test", follow_redirects=False)

        assert response.status_code == 302
        assert response.headers["location"] == "https://redirect-target.com/"

    async def test_redirect_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent slug."""
        response = await client.get("/nonexistent-redirect")

        assert response.status_code == 404

    async def test_redirect_increments_click_count(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should increment click count on redirect."""
        # Create a link
        link_data = {
            "original_url": "https://click-count.com",
            "slug": "click-count-test",
        }
        create_response = await client.post(
            "/api/v1/links/", json=link_data, headers=auth_headers
        )
        initial_count = create_response.json()["click_count"]

        # Access the link
        await client.get("/click-count-test", follow_redirects=False)

        # Check click count increased
        get_response = await client.get("/api/v1/links/click-count-test")
        assert get_response.json()["click_count"] == initial_count + 1
