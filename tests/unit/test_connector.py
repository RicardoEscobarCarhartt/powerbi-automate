"""This module contains unit tests for the connector module."""

from unittest.mock import Mock, patch

import pytest

from carhartt_pbi_automate.connector import (
    get_bi_connection,
    get_edw_connection,
)


@pytest.mark.unit
def test_get_edw_connection(
    mock_engine_mock_create_engine,
):
    """Tests the get_edw_connection function."""
    # Unpack fixtures
    mock_engine, mock_create_engine = mock_engine_mock_create_engine

    # Arguments and expected result
    args = {
        "server": "server",
        "database": "database",
        "driver": "driver",
    }
    expected_connection_string = f"mssql+pyodbc://{args["server"]}/{args["database"]}?driver={args["driver"]}&trusted_connection=yes"

    # Act
    result = get_edw_connection(args)

    # Asserts
    # Assert create_engine was called with the expected connection string
    mock_create_engine.assert_called_with(
        expected_connection_string, fast_executemany=True
    )

    # Assert the result is the connection returned by the engine
    assert result == mock_engine.connect.return_value


@pytest.fixture(scope="function")
def mock_connect():
    """Mock the adodbapi.connect function."""
    with patch(
        "carhartt_pbi_automate.connector.adodbapi.connect"
    ) as mock_connect:  # pylint: disable=W0621
        yield mock_connect


@pytest.fixture(scope="function")
def mock_connection_mock_connect(
    mock_connect,
):  # pylint: disable=W0621
    """Fixture for mocking the adodbapi.connect function."""
    # Mock connect return value
    mock_connection = Mock()
    mock_connect.return_value = mock_connection
    yield mock_connection, mock_connect


@pytest.mark.unit
def test_get_bi_connection(
    mock_connection_mock_connect,
):  # pylint: disable=W0621
    """Tests the get_bi_connection function."""
    # Unpack fixtures
    mock_connection, mock_connect = (
        mock_connection_mock_connect  # pylint: disable=W0621
    )

    # Arguments and expected result
    server = "server"
    database = "database"
    expected_connection_string = (
        f"Provider=MSOLAP.8; Data Source={server}; Initial Catalog={database};"
    )

    # Act
    result = get_bi_connection(server, database)

    # Asserts
    # Assert the result is a connection
    assert result == mock_connection

    # Assert connect was called with the expected connection string
    mock_connect.assert_called_with(expected_connection_string)


if __name__ == "__main__":
    pytest.main()
