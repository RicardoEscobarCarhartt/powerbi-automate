"""This module contains unit tests for the get_formated_duration module."""

import pytest

from carhartt_pbi_automate.get_formated_duration import get_formated_duration


@pytest.mark.unit
def test_get_formated_duration_int():
    """Test the get_formated_duration function."""
    # test with a timedelta object
    duration = get_formated_duration(3661)
    assert duration == "01:01:01"
