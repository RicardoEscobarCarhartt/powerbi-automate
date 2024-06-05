"""This module contains unit tests for the parse_arguments module."""

from unittest.mock import patch
import argparse

import pytest

from carhartt_pbi_automate.parse_arguments import parse_arguments


@patch("argparse.ArgumentParser.add_argument")
@patch("argparse.ArgumentParser.parse_args")
@pytest.mark.unit
def test_parse_arguments(mock_parse_args, mock_add_argument):
    """Test the parse_arguments function."""
    # Mock `parse_args` call
    mock_parse_args.assert_called_once()

    # Mock `add_argument` calls
    mock_add_argument.assert_any_call(
        "--daxfile",
        type=str,
        default=r"C:\Users\rescobar\OneDrive - Carhartt Inc\Documents\git\powerbi-automate\queries\supply.dax",
        help="File path to DAX query",
    )

    mock_add_argument.assert_any_call(
        "--sqlfile",
        type=str,
        default=r"C:\Users\rescobar\OneDrive - Carhartt Inc\Documents\git\powerbi-automate\queries\supply.sql",
        help="File path to SQL query",
    )


@pytest.mark.parametrize(
    ["daxfile_arg", "sqlfile_arg"],
    [
        (None, "sqlfile"),
        ("daxfile", None),
        (None, None),
    ],
)
@pytest.mark.unit
def test_parse_arguments_raises_exception(daxfile_arg, sqlfile_arg):
    """Test the return type of the parse_arguments function."""
    # Patching the `argparse.ArgumentParser.parse_args` method to raise an exception
    with patch(
        "argparse.ArgumentParser.parse_args",
        side_effect=argparse.ArgumentError(None, None),
    ):
        with pytest.raises(argparse.ArgumentError):
            parse_arguments()

    # Modify arguments to raise a different exception
    args = argparse.Namespace()
    args.daxfile = daxfile_arg
    args.sqlfile = sqlfile_arg

    # Patching the `argparse.ArgumentParser.parse_args` method to return the modified arguments
    with patch("argparse.ArgumentParser.parse_args", return_value=args):
        with pytest.raises(ValueError):
            parse_arguments()
