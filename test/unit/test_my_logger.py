import unittest
import logging
from pathlib import Path

from carhartt_pbi_automate.my_logger import MyLogger


class TestMyLogger(unittest.TestCase):
    def setUp(self):
        self.log_file = Path("logs/test/test_my_logger.log")
        self.logger = MyLogger("test.unit.test_my_logger", self.log_file)

    def tearDown(self):
        self.logger.close()
        self.log_file.unlink(missing_ok=True)

    def test_logger_init(self):
        self.assertIsInstance(self.logger, MyLogger)
        self.assertEqual(self.logger.name, "test.unit.test_my_logger")
        self.assertEqual(self.logger.log_file, self.log_file)
        self.assertTrue(self.log_file.exists())

    def test_logger_init_console_file_optional(self):
        """Test that the stream handler is not used if the console_log, file_log attributes is set to False"""
        self.logger.console_log = False
        for handler in self.logger.handlers:
            self.assertNotIsInstance(handler, logging.StreamHandler)
        self.logger.info("This is a test, this message should not be printed to the console")



    def test_logger_logging(self):
        self.logger.info("This is a test")
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("This is a test", content)


if __name__ == "__main__":
    unittest.main()