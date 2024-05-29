"""This module contains unit tests for the database module."""

from unittest.mock import Mock, patch

import pytest

from carhartt_pbi_automate.database import Database


@pytest.fixture
def db_file():
    """Fixture to create a Database file using the Database class."""
    db = Database(db_file="test.db")
    return db


def test_create_database_object():
    """Tests the Database class."""
    # SQLite3 connection allows for a database to be created in memory, I use
    # this to test the Database class without creating a file or mocking the
    # sqlite3 module.

    # Arrange and Act
    db = Database()

    # Assert
    # Assert the db_file is ":memory:"
    assert db.db_file == ":memory:"


if __name__ == "__main__":
    pytest.main()
