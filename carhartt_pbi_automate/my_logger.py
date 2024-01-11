"""This module creates a logger for the application."""
import logging
from pathlib import Path


class MyLogger(logging.Logger):
    """This class represents the logger for the application."""

    def __init__(self, name: str, log_file: Path, level: int = logging.INFO):
        """Initialize the logger."""
        super().__init__(name, level)
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create a file handler to write to the log file
        self.file_handler = logging.FileHandler(self.log_file)
        self.file_handler.setLevel(level)
        self.file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.file_handler.setFormatter(self.file_formatter)

        # Create a stream handler to print to stdout
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(level)
        self.stream_formatter = logging.Formatter("%(message)s")
        self.stream_handler.setFormatter(self.stream_formatter)
        self.addHandler(self.file_handler)
        self.addHandler(self.stream_handler)

        self.info("Logger initialized")

    def close(self):
        """Close the logger."""
        self.info("Logger closed")
        self.removeHandler(self.file_handler)
        self.file_handler.close()
        self.removeHandler(self.stream_handler)
        self.stream_handler.close()

if __name__ == "__main__":
    # This code is executed when the file is run from the command line
    logger = MyLogger("test", Path("test.log"))
    logger.info("This is a test")
    logger.close()