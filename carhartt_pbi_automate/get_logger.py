"""This module contains functions that create and return a logger object."""

from pathlib import Path
from typing import Union
import logging


def get_logger(
    name: str,
    logfile: Union[Path, str] = None,
    level: int = logging.DEBUG,
    console_output: bool = True,
) -> logging.Logger:
    """
    Get a logger object.
    Args:
        name (str): The name of the logger.
        logfile (Union[Path, str], optional): The logfile path. Defaults to None.
        level (int, optional): The logging level. Defaults to logging.DEBUG.
        console_output (bool, optional): Whether to output logs to the console.
    Returns:
        logging.Logger: The logger object.
    """
    # Initialize the logfile if it is not provided
    if not logfile:
        logfile = f"{name}.log"

    # create a logger object
    created_logger = logging.getLogger(name)

    # set the logging level
    created_logger.setLevel(level)

    # create a formatter
    format_string = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
    formatter = logging.Formatter(format_string)

    # Create the file if it does not exist, and write the column names
    touch_file(logfile, format_string)

    # create a file handler
    file_handler = logging.FileHandler(logfile)

    # set the formatter
    file_handler.setFormatter(formatter)

    # set the logging level for the file handler
    file_handler.setLevel(logging.DEBUG)

    # If console_output is True, create a console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        created_logger.addHandler(console_handler)

    # add the file handler to the logger
    created_logger.addHandler(file_handler)
    return created_logger


def touch_file(filepath: Union[Path, str], columns: str) -> str:
    """
    Create an empty file if it does not exist.
    Args:
        filepath (Union[Path, str]): The file path.
        columns (str): The column names.
    """
    # Remove "%(", ")s" from the columns
    columns = columns.replace("%(", "").replace(")s", "")

    # Create the directory if it does not exist
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    # Create the file if it does not exist
    if not Path(filepath).exists():
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(columns + "\n")
    return filepath


if __name__ == "__main__":
    # Send log messages
    logger = get_logger("test", "logs/test.log")
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
