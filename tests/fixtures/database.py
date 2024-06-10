"""Fixtures for test_database.py"""

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def db_path():
    """Returns a temporary file path for the database."""
    return "test.db"


@pytest.fixture(scope="module")
def script_path(db_path):  # pylint: disable=W0621
    """Returns a temporary SQL script file path."""
    sql_script = db_path.replace(".db", ".sql")
    return sql_script


# This fixture creates a temporary SQL script file
@pytest.fixture(scope="function")
def get_script(script_path):  # pylint: disable=W0621
    """Creates a temporary SQL script file."""
    with open(script_path, "w", encoding="utf-8") as file:
        file.write(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);"
        )

    # Return the script path, must be outside the with block to allow the file
    # to be closed before the path is returned
    yield script_path

    # Clean up
    Path(script_path).unlink(missing_ok=True)


# Remove the 'test.db' file after the tests are done
@pytest.fixture(scope="function", autouse=True)
def remove_db_file(db_path):  # pylint: disable=W0621
    """Removes the test database file."""
    yield
    # Clean up
    Path(db_path).unlink(missing_ok=True)
