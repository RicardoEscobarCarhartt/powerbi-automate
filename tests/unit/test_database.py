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


@pytest.mark.unit
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


@pytest.mark.unit
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

    # Close the database connection
    db.close()


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_create_database_object_with_invalid_db_file_type(
    get_script,
):  # pylint: disable=W0621
    """Tests the Database class with an invalid db_file type."""
    # Assert raises a TypeError if db_file is not a Path or str
    with pytest.raises(TypeError) as exc:
        Database(db_file=1, initial_sql_script=get_script)

    # Assert the error message
    assert f"db_file must be a Path or str. Not {type(1)}" in str(exc.value)


@pytest.mark.unit
def test_create_table(db_path, get_script):  # pylint: disable=W0621
    """Tests the create_table method."""
    # Arrange
    db = Database(db_path, get_script)
    table_name = "new_table"
    columns = ["id INTEGER PRIMARY KEY", "name TEXT"]
    sql_query = "SELECT name FROM sqlite_master WHERE type='table';"

    # Act
    db.create_table(table_name, columns)

    # Assert
    # Assert the table was created
    db.open()
    db.cursor.execute(sql_query)
    tables = db.cursor.fetchall()
    for table in tables:
        if table == table_name:
            assert table == table_name

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_insert(db_path, get_script):  # pylint: disable=W0621
    """Tests the insert method."""
    # Arrange
    # the `db.cursor.execute(sql_query)` line is executed
    db = Database(db_path, get_script)

    assert get_script == "test.sql"
    table_name = "test_table"
    columns = ["id", "name"]
    values = (
        1,
        "test",
    )
    sql_query = "SELECT * FROM test_table;"

    # Act
    db.insert(table_name, columns, values)

    # Assert
    # Assert the row was inserted
    db.open()
    db.cursor.execute(sql_query)
    rows = db.cursor.fetchall()
    for row in rows:
        if row == values:
            assert row == values

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_select(db_path, get_script):  # pylint: disable=W0621
    """Tests the select method."""
    # Arrange
    db = Database(db_path, get_script)
    table_name = "test_table"
    columns = ["id", "name"]
    values = (
        1,
        "test",
    )
    where = "id = 1"
    sql_query = "SELECT * FROM test_table WHERE id = 1;"

    # Act
    db.insert(table_name, columns, values)
    result = db.select(table_name, where=where, columns=columns)

    # Assert
    # Assert the row was selected
    db.open()
    db.cursor.execute(sql_query)
    row = db.cursor.fetchone()
    assert tuple(row) == values

    # Convert the result to a list of tuples
    result = [tuple(row) for row in result]

    # Assert the result is the same as the row
    assert result == [values]

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_update(db_path, get_script):  # pylint: disable=W0621
    """Tests the update method."""
    # Arrange
    db = Database(db_path, get_script)
    table_name = "test_table"
    columns = ["id", "name"]
    values = (1, "name")
    new_values = (1, "new_name")
    where = "id = 1"
    sql_query = "SELECT name FROM test_table WHERE id = 1;"

    # Act
    db.insert(table_name, columns, values)
    db.update(table_name, columns, new_values, where)

    # Assert
    # Assert the row was updated
    db.open()
    db.cursor.execute(sql_query)
    row = db.cursor.fetchone()
    assert row[0] == new_values[1]

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_delete(db_path, get_script):  # pylint: disable=W0621
    """Tests the delete method."""
    # Arrange
    db = Database(db_path, get_script)
    table_name = "test_table"
    columns = ["id", "name"]
    values = (
        1,
        "test",
    )
    where = "id = 1"
    sql_query = "SELECT * FROM test_table WHERE id = 1;"

    # Act
    db.insert(table_name, columns, values)
    db.delete(table_name, where)

    # Assert
    # Assert the row was deleted
    db.open()
    db.cursor.execute(sql_query)
    row = db.cursor.fetchone()
    assert row is None

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_open(db_path, get_script):  # pylint: disable=W0621
    """Tests the open method."""
    # Arrange
    db = Database(db_path, get_script)

    # Act
    db.open()

    # Assert
    # Assert the connection is open
    assert db.conn is not None

    # Assert the cursor is open
    assert db.cursor is not None

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_close(db_path, get_script):  # pylint: disable=W0621
    """Tests the close method."""
    # Arrange
    db = Database(db_path, get_script)

    # Act
    db.open()
    db.close()

    # Assert
    # Assert the connection is closed
    assert db.conn is None


@pytest.mark.unit
def test_get_columns(db_path, get_script):  # pylint: disable=W0621
    """Tests the get_columns method."""
    # Arrange
    db = Database(db_path, get_script)
    table_name = "test_table"
    columns = ["id INTEGER PRIMARY KEY", "name TEXT"]
    sql_query = "PRAGMA table_info(test_table);"

    # Act
    result = db.get_columns(table_name)

    # Assert
    # Assert the columns are returned
    db.open()
    db.cursor.execute(sql_query)
    rows = db.cursor.fetchall()
    columns = [row["name"] for row in rows]
    assert columns == result

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_get_columns_with_invalid_table_name(
    db_path, get_script
):  # pylint: disable=W0621
    """Tests the get_columns method with an invalid table name."""
    # Arrange
    db = Database(db_path, get_script)
    table_name = "invalid_table"

    # Act
    result = db.get_columns(table_name)

    # Assert
    # Assert the columns are returned
    assert result == []

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_get_columns_with_invalid_table_name_type(
    db_path, get_script
):  # pylint: disable=W0621
    """Tests the get_columns method with an invalid table name type."""
    # Arrange
    db = Database(db_path, get_script)
    table_name = 1

    # Act
    with pytest.raises(TypeError) as exc:
        result = db.get_columns(table_name)
        assert result == []

    # Assert
    # Assert the error message
    assert f"table_name must be a str. Not {type(1)}" in str(exc.value)

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_get_tables(db_path, get_script):  # pylint: disable=W0621
    """Tests the get_tables method."""
    # Arrange
    db = Database(db_path, get_script)
    sql_query = "SELECT name FROM sqlite_master WHERE type='table';"

    # Act
    result = db.get_tables()

    # Assert
    # Assert the tables are returned
    db.open()
    db.cursor.execute(sql_query)
    tables = db.cursor.fetchall()
    tables = [table["name"] for table in tables]
    assert tables == result

    # Close the database connection
    db.close()


@pytest.mark.unit
def test_table_exists(db_path, get_script):  # pylint: disable=W0621
    """Tests the table_exists method."""
    # Arrange
    db = Database(db_path, get_script)
    table_name = "test_table"

    # Act
    result = db.table_exists(table_name)

    # Assert
    # Assert the table exists
    assert result

    # Close the database connection
    db.close()


if __name__ == "__main__":
    pytest.main()
