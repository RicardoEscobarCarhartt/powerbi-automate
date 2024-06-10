"""Fixtures for get_formated_duration tests."""

from datetime import timedelta

import pytest


@pytest.fixture(scope="function")
def int_arg():
    """Return a duration as an int."""
    return 3661


@pytest.fixture(scope="function")
def td_arg():
    """Return a duration as a timedelta object."""
    return timedelta(seconds=3661)
