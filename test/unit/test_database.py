"""This module tests the database.py module."""
import unittest
from pathlib import Path

from carhartt_pbi_automate.database import Database


class TestDatabase(unittest.TestCase):
    """Test the Database class."""

    def setUp(self):
        """Set up the test."""
        self.db = Database(":memory:")

    def tearDown(self):
        """Tear down the test."""
        self.db.close()
        if isinstance(self.db.db_file, Path):
            self.db.db_file.unlink(missing_ok=True)

    def test_database_init(self):
        """Test the Database.__init__ method."""
        self.assertIsInstance(self.db, Database)
        self.assertEqual(self.db.db_file, ":memory:")

        # Test that the database file is created if a file path is passed as str
        self.db = Database("test.db")
        self.assertEqual(str(self.db.db_file), "test.db")
        self.assertTrue(self.db.db_file.exists())
        self.db.close()

        # Test that the database file is created if a file path is passed as Path
        self.db = Database(Path("test.db"))
        self.assertEqual(str(self.db.db_file), "test.db")
        self.db.close()

        # Test that the exepction is raised if db_file is not a Path or str
        with self.assertRaises(TypeError):
            Database(1)

    def test_create_table(self):
        """Test the create_table method."""
        self.db.create_table("test", ["id INTEGER PRIMARY KEY", "name TEXT"])
        self.db.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = self.db.cursor.fetchall()
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["name"], "test")

    def test_insert(self):
        """Test the insert method."""
        self.db.create_table("test", ["id INTEGER PRIMARY KEY", "name TEXT"])
        self.db.insert("test", ["name"], ["test"])
        self.db.cursor.execute("SELECT * FROM test")
        rows = self.db.cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "test")

    def test_select(self):
        """Test the select method."""
        self.db.create_table("test", ["id INTEGER PRIMARY KEY", "name TEXT"])
        self.db.insert("test", ["name"], ["test"])
        rows = self.db.select("test", ["name"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "test")

    def test_update(self):
        """Test the update method."""
        self.db.create_table("test", ["id INTEGER PRIMARY KEY", "name TEXT"])
        self.db.insert("test", ["name"], ["test"])
        self.db.update("test", ["name"], ["test2"])
        rows = self.db.select("test", ["name"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "test2")

    def test_delete(self):
        """Test the delete method."""
        self.db.create_table("test", ["id INTEGER PRIMARY KEY", "name TEXT"])
        self.db.insert("test", ["name"], ["test"])
        self.db.delete("test")
        rows = self.db.select("test", ["name"])
        self.assertEqual(len(rows), 0)


if __name__ == "__main__":
    unittest.main()
