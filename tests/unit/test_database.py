"""This module contains unit tests for the database module."""

from pathlib import Path

import pytest

from carhartt_pbi_automate.database import Database


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
@pytest.fixture(scope="module")
def get_script(script_path):  # pylint: disable=W0621
    """Creates a temporary SQL script file."""
    with open(script_path, "w", encoding="utf-8") as file:
        file.write(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);"
        )
        yield script_path

    # Clean up
    Path(script_path).unlink()


# Remove the 'test.db' file after the tests are done
@pytest.fixture(scope="module", autouse=True)
def remove_db_file(db_path):  # pylint: disable=W0621
    """Removes the test database file."""
    yield

    # Clean up
    Path(db_path).unlink()


def test_create_database_object(get_script):  # pylint: disable=W0621
    """Tests the Database class."""
    # SQLite3 connection allows for a database to be created in memory, I use
    # this to test the Database class without creating a file or mocking the
    # sqlite3 module.

    # Arrange and Act
    db = Database(initial_sql_script=get_script)

    # Assert
    # Assert the db_file is ":memory:"
    assert db.db_file == ":memory:"

    # Assert the db_file is a Path object
    assert isinstance(db.db_file, str)


# @pytest.mark.skip(reason="This test is not working")
def test_create_database_object_with_file(
    db_path, get_script
):  # pylint: disable=W0621
    """Tests the Database class with an initial sql script file."""
    # Arrange and Act
    db = Database(db_file=db_path, initial_sql_script=get_script)

    # Assert
    # Assert the db_file is a Path object
    assert isinstance(db.db_file, Path)

    # Assert the db_file exists
    assert db.db_file.exists()

    # Assert the db_file is a file
    assert db.db_file.is_file()


def test_create_database_object_with_missing_initial_sql_script(
    db_path,
):  # pylint: disable=W0621
    """Tests the Database class with a missing initial sql script."""
    # Assert raises a ValueError if initial_sql_script does not exist
    with pytest.raises(ValueError) as exc:
        Database(db_file=db_path)

    # Assert the error message
    assert "initial_sql_script not provided, must be a Path or str." in str(
        exc.value
    )


def test_create_database_object_with_invalid_initial_sql_script_type(
    db_path,
):  # pylint: disable=W0621
    """Tests the Database class with an invalid initial sql script."""
    # Assert raises a TypeError if initial_sql_script is not a Path or str
    with pytest.raises(TypeError) as exc:
        Database(db_file=db_path, initial_sql_script=1)

    # Assert the error message
    assert f"initial_sql_script must be a Path or str. Not {type(1)}" in str(
        exc.value
    )


def test_create_database_object_validating_parent_directory(
    db_path, get_script
):  # pylint: disable=W0621
    """Tests the Database class with a valid parent directory."""
    # Arrange and Act
    db = Database(db_file=db_path, initial_sql_script=get_script)

    # Assert
    # Assert the db_file is a Path object
    assert isinstance(db.db_file, Path)

    # Assert the db_file exists
    assert db.db_file.exists()

    # Assert the db_file is a file
    assert db.db_file.is_file()

    # Assert the parent directory exists
    assert db.db_file.parent.exists()

    # Assert the db file exists
    assert db.db_file.exists()


def test_create_database_object_with_invalid_db_file_type(get_script):  # pylint: disable=W0621
    """Tests the Database class with an invalid db_file type."""
    # Assert raises a TypeError if db_file is not a Path or str
    with pytest.raises(TypeError) as exc:
        Database(db_file=1, initial_sql_script=get_script)

    # Assert the error message
    assert f"db_file must be a Path or str. Not {type(1)}" in str(exc.value)

if __name__ == "__main__":
    pytest.main()
