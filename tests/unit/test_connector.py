"""This module contains unit tests for the connector module."""

import pytest
from unittest.mock import Mock, patch

from carhartt_pbi_automate.connector import (
    get_bi_connection,
    get_edw_connection,
)



@patch("carhartt_pbi_automate.connector.create_engine")
def test_get_edw_connection(mock_create_engine):
    """Tests the get_edw_connection function."""
    # Mock create_engine return value
    mock_engine = Mock()
    mock_engine.connect.return_value = Mock()
    mock_create_engine.return_value = mock_engine


    # Arguments and expected result
    args = {
        "server": "server",
        "database": "database",
        "driver": "driver",
    }
    expected_connection_string = f"mssql+pyodbc://{args["server"]}/{args["database"]}?driver={args["driver"]}&trusted_connection=yes"

    # Act
    result = get_edw_connection(args)

    # Assert
    # engine = create_engine(connection_string, fast_executemany=True)
    mock_create_engine.assert_called_with(expected_connection_string, fast_executemany=True)

    # Assert
    # return engine.connect()
    assert result == mock_engine.connect.return_value
    

if __name__ == "__main__":
    pytest.main()
