"""This module tests the database.py module."""
import unittest

from carhartt_pbi_automate.database import Database


class TestDatabase(unittest.TestCase):
    """Test the Database class."""

    def setUp(self):
        """Set up the test."""
        self.db = Database(":memory:")

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
