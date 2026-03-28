"""Integration tests for analytics endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestGetLinkStats:
    """Tests for GET /api/v1/analytics/{slug}."""

    async def test_get_stats_success(self, client: AsyncClient, auth_headers: dict):
        """Should return link statistics."""
        # Create a link
        link_data = {
            "original_url": "https://analytics-test.com",
            "slug": "analytics-test",
        }
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        response = await client.get(
            "/api/v1/analytics/analytics-test", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "analytics-test"
        assert data["original_url"] == "https://analytics-test.com/"
        assert "total_clicks" in data
        assert "clicks" in data
        assert isinstance(data["clicks"], list)

    async def test_get_stats_requires_auth(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.get("/api/v1/analytics/some-slug")

        assert response.status_code == 401

    async def test_get_stats_not_found(self, client: AsyncClient, auth_headers: dict):
        """Should return 404 for non-existent link."""
        response = await client.get(
            "/api/v1/analytics/nonexistent-analytics", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_get_stats_forbidden_for_other_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        another_auth_headers: dict,
    ):
        """Should forbid accessing another user's link stats."""
        # Create link as first user
        link_data = {
            "original_url": "https://example.com",
            "slug": "private-stats",
        }
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        # Try to access stats as second user
        response = await client.get(
            "/api/v1/analytics/private-stats", headers=another_auth_headers
        )

        assert response.status_code == 403

    async def test_get_stats_with_clicks(self, client: AsyncClient, auth_headers: dict):
        """Should return stats with click data after visits."""
        # Create a link
        link_data = {
            "original_url": "https://click-stats-test.com",
            "slug": "click-stats-test",
        }
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        # Generate some clicks
        await client.get("/click-stats-test", follow_redirects=False)
        await client.get("/click-stats-test", follow_redirects=False)

        # Get stats
        response = await client.get(
            "/api/v1/analytics/click-stats-test", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_clicks"] == 2
        assert len(data["clicks"]) == 2

    async def test_get_stats_click_details(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should include click details (device_type, etc.)."""
        # Create a link
        link_data = {
            "original_url": "https://details-test.com",
            "slug": "details-test",
        }
        await client.post("/api/v1/links/", json=link_data, headers=auth_headers)

        # Generate a click with custom user-agent
        await client.get(
            "/details-test",
            follow_redirects=False,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )

        # Get stats
        response = await client.get(
            "/api/v1/analytics/details-test", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["clicks"]) == 1

        click = data["clicks"][0]
        assert "clicked_at" in click
        assert "device_type" in click
        assert "country" in click
        assert "referer" in click


@pytest.mark.asyncio
class TestHealthCheck:
    """Tests for GET /health."""

    async def test_health_check(self, client: AsyncClient):
        """Should return healthy status."""
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "online"}
