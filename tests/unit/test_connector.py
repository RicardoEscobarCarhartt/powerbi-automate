"""This module contains unit tests for the connector module."""

import pytest
from unittest.mock import Mock, patch

from carhartt_pbi_automate.connector import (
    get_bi_connection,
    get_edw_connection,
)


# "sqlalchemy.engine.create.create_engine" is the full path to the function
# that needs to be patched
@patch("sqlalchemy.engine.base.Connection")
@patch("sqlalchemy.engine.create.create_engine")
def test_get_edw_connection(mock_create_engine, mock_connection):
    """Tests the get_edw_connection function."""
    # Create a mock engine with a connect method
    mock_engine = Mock()
    # mock_connection = Mock()
    mock_engine.connect.return_value = mock_connection
    mock_create_engine.return_value = mock_engine

    args = {
        "server": "server",
        "database": "database",
        "driver": "driver",
    }
    # Call the function with the mocked engine
    result = get_edw_connection(args)
    # Assert that the connect method was called on the mocked engine
    assert mock_engine.connect.called
    # Assert that the result is the mocked connection
    assert result == mock_connection



if __name__ == "__main__":
    pytest.main()
