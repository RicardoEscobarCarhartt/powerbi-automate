"""This module contains unit tests for the get_formated_duration module."""

from datetime import timedelta

import pytest

from carhartt_pbi_automate.get_formated_duration import get_formated_duration


@pytest.fixture(scope="function")
def int_arg():
    """Return a duration as an int."""
    return 3661


@pytest.fixture(scope="function")
def td_arg():
    """Return a duration as a timedelta object."""
    return timedelta(seconds=3661)


@pytest.mark.unit
def test_get_formated_duration_int(int_arg):  # pylint: disable=W0621
    """Test the get_formated_duration function."""
    # test with a timedelta object
    actual = get_formated_duration(int_arg)
    expected = "01:01:01"
    assert actual == expected


@pytest.mark.unit
def test_get_formated_duration_td(td_arg):  # pylint: disable=W0621
    """Test the get_formated_duration function."""
    # test with a timedelta object
    actual = get_formated_duration(td_arg)
    expected = "01:01:01"
    assert actual == expected


@pytest.mark.unit
def test_get_formated_duration_invalid_arg():
    """Test the get_formated_duration function."""
    # test with an invalid argument
    with pytest.raises(TypeError) as excinfo:
        get_formated_duration("invalid")

    # check the error message
    expected = "Invalid argument type. Must be an int or timedelta object."
    assert str(excinfo.value) == expected


@pytest.mark.unit
def test_get_formated_duration_show_seconds():
    """Test the get_formated_duration function when the amount of seconds is less than 60."""
    # test with a timedelta object
    actual = get_formated_duration(59)
    expected = "59 seconds"
    assert actual == expected


@pytest.mark.unit
def test_get_formated_duration_show_minutes():
    """Test the get_formated_duration function when the amount of seconds is less than 3600."""
    # test with a timedelta object
    actual = get_formated_duration(3599)
    expected = "59:59"
    assert actual == expected


@pytest.mark.unit
def test_get_formated_duration_show_hours():
    """Test the get_formated_duration function when the amount of seconds is greater than 3600."""
    # test with a timedelta object
    actual = get_formated_duration(3601)
    expected = "01:00:01"
    assert actual == expected