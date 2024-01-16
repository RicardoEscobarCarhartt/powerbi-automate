"""This module contains unit tests for the SqliteHandler class."""
import unittest
import logging
from pathlib import Path

from carhartt_pbi_automate.database import Database
from carhartt_pbi_automate.my_logger import MyLogger

class TestSqliteHandler(unittest.TestCase):
    """Test the SqliteHandler class."""
    def setUp(self):
        self.log_file = Path("logs/test/test_sqlite_handler.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        sqlite_script = Path("database/logging.sql")
        test_db = Path("database/test_sqlite_handler.db")
        self.database = Database(test_db, sqlite_script)
        self.logger = MyLogger(
            "test.unit.test_my_logger",
            self.log_file,
            logging.DEBUG,
            log_to_console=False,
            log_to_file=True,
            log_to_database=True,
            database=self.database,
        )

    def tearDown(self):
        self.logger.close()
        self.database.close()
        self.log_file.unlink()
        # self.database.db_file.unlink()

    def test_emit(self):
        """Test that the emit method is working correctly"""
        self.logger.info("Test message")
        sql_query = "SELECT * FROM log_record where message = 'Test message'"
        cursor = self.database.cursor.execute(sql_query)
        row = cursor.fetchone()
        self.assertEqual(row["message"], "Test message")
        
if __name__ == "__main__":
    unittest.main()
