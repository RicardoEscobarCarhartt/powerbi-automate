"""Fixtures for DAX tests."""

import pytest


@pytest.fixture(scope="module")
def dax_query():
    """Returns a str containing a DAX query."""
    return """
    EVALUATE
    { "Hello, "&@test_parameter }
    """.strip()


@pytest.fixture(scope="module")
def non_string_args():
    """Returns a dict containing non-string arguments."""

    class NonString:
        def __str__(self):
            return "NonString"

    return {"test_parameter": NonString()}
