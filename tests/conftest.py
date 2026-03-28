"""Root test configuration - minimal, no database fixtures."""

import pytest


# Configure pytest-asyncio for async tests
@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio for async tests."""
    return "asyncio"
