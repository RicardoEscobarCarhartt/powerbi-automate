"""Fixtures for the connector module."""

from unittest.mock import Mock, patch

import pytest

@pytest.fixture(scope="function")
def mock_create_engine():
    """Fixture for mocking the create_engine function."""
    with patch(
        "carhartt_pbi_automate.connector.create_engine"
    ) as _mock_create_engine:
        yield _mock_create_engine


@pytest.fixture(scope="function")
def mock_engine_mock_create_engine(
    mock_create_engine,
):  # pylint: disable=W0621
    """Fixture for mocking the create_engine function."""
    # Mock create_engine return value
    mock_engine = Mock()
    mock_engine.connect.return_value = Mock()
    mock_create_engine.return_value = mock_engine
    yield mock_engine, mock_create_engine
