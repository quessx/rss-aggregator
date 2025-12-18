"""Pytest configuration and fixtures."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def mock_actor():
    """Mock Apify Actor for testing."""
    mock = MagicMock()
    mock.log.info = MagicMock()
    mock.log.warning = MagicMock()
    mock.log.error = MagicMock()
    mock.log.debug = MagicMock()
    mock.sleep = MagicMock()
    return mock

