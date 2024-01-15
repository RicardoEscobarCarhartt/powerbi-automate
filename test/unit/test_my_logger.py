import unittest
import logging
from pathlib import Path

from carhartt_pbi_automate.my_logger import MyLogger
from carhartt_pbi_automate.sqlite_handler import SqliteHandler


class TestMyLogger(unittest.TestCase):
    def setUp(self):
        self.log_file = Path("logs/test/test_my_logger.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = MyLogger("test.unit.test_my_logger", self.log_file)

    def tearDown(self):
        self.logger.close()
        # self.log_file.unlink(missing_ok=True)

    def test_logger_init(self):
        """Test that the logger is initialized correctly"""
        self.assertIsInstance(self.logger, MyLogger)
        self.assertEqual(self.logger.name, "test.unit.test_my_logger")
        self.assertEqual(self.logger.log_file, self.log_file)
        self.assertTrue(self.log_file.exists())

    def test_logger_optional_logging(self):
        """Test that the stream handler is not used if the console_log, file_log attributes is set to False"""
        # Test that the stream handler is not used if the console_log attribute is set to False
        self.logger.console_log = False
        if self.logger.stream_handler:
            self.logger.stream_handler.setLevel(logging.WARNING)
        for handler in self.logger.handlers:
            self.assertIsNot(handler, logging.StreamHandler)

        self.logger.info(
            "This is a test, this message should not be printed to the console"
        )

        # Test that the file handler is not used if the file_log attribute is set to False
        self.logger.file_log = False
        if self.logger.file_handler:
            self.logger.file_handler.setLevel(logging.WARNING)
        for handler in self.logger.handlers:
            self.assertIsNot(handler, logging.FileHandler)

        self.logger.info(
            "This is a test, this message should not be written to a file"
        )

        # Test that the sqlite handler is not used if the database_log attribute is set to False
        self.logger.database_log = False
        if self.logger.sqlite_handler:
            self.logger.sqlite_handler.setLevel(logging.WARNING)
        for handler in self.logger.handlers:
            self.assertIsNot(handler, SqliteHandler)

        self.logger.info(
            "This is a test, this message should not be written to the database"
        )

    def test_logger_logging(self):
        """Test that the logger is logging correctly"""
        self.logger.info("This is a test")
        with open(self.log_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("This is a test", content)


if __name__ == "__main__":
    unittest.main()
