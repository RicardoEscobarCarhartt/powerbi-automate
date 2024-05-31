"""This module contains unit tests for the dax module."""

import pytest

from carhartt_pbi_automate.dax import pass_args_to_dax_query


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


def test_pass_args_to_dax_query(
    dax_query, non_string_args
):  # pylint: disable=W0621
    """Tests the pass_args_to_dax_query function."""
    # Test passing a string argument
    args = {"test_parameter": "World."}
    expected = """
    EVALUATE
    { "Hello, "&"World." }
    """.strip()
    assert pass_args_to_dax_query(dax_query, args) == expected

    # Test passing a numeric argument
    args = {"test_parameter": 1}
    expected = """
    EVALUATE
    { "Hello, "&1 }
    """.strip()
    assert pass_args_to_dax_query(dax_query, args) == expected

    # Test passing a boolean argument, not a string or number
    # This works as long as the value has a __str__ method
    args = {"test_parameter": True}
    expected = """
    EVALUATE
    { "Hello, "&"True" }
    """.strip()
    actual = pass_args_to_dax_query(dax_query, args)
    assert actual == expected

    # Test passing a non-string argument
    args = non_string_args
    expected = """
    EVALUATE
    { "Hello, "&"NonString" }
    """.strip()
    actual = pass_args_to_dax_query(dax_query, args)
    assert actual == expected


if __name__ == "__main__":
    pytest.main()
