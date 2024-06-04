"""This is a conftest.py file that contains fixtures for the unit tests."""

from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def project_root():
    """Return the project root."""
    yield Path(__file__).parent.parent.parent
