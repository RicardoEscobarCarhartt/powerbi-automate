"""This is a conftest.py file that contains fixtures for the unit tests."""

from pathlib import Path

import pytest


# Global fixtures
@pytest.fixture(scope="function")
def project_root() -> Path:
    """Return the project root."""
    return Path(__file__).parent.parent


# Modulirized fixtures
pytest_plugins = [
    "tests.fixtures.get_logger",
    "tests.fixtures.my_logger",
    "tests.fixtures.sqlite_handler",
    "tests.fixtures.connector",
    "tests.fixtures.database",
]
