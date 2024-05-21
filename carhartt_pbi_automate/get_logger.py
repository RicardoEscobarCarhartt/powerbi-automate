"""This module contains functions that create and return a logger object."""

from pathlib import Path
from typing import Union
import logging


def get_logger(
    name: str, logfile: Union[Path, str] = None, level: int = logging.DEBUG
) -> logging.Logger:
    """
    Get a logger object.
    Args:
        name (str): The name of the logger.
        logfile (Union[Path, str], optional): The logfile path. Defaults to None.
        level (int, optional): The logging level. Defaults to logging.DEBUG.
    Returns:
        logging.Logger: The logger object.
    """
    # Initialize the logfile if it is not provided
    if not logfile:
        logfile = f"{name}.log"

    # create a logger object
    logger = logging.getLogger(name)

    # set the logging level
    logger.setLevel(level)

    # create a file handler
    file_handler = logging.FileHandler(logfile)

    # create a formatter
    format_string = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
    formatter = logging.Formatter(format_string)

    # Create the file if it does not exist, and write the column names
    touch_file(logfile, format_string)

    # set the formatter
    file_handler.setFormatter(formatter)

    # add the file handler to the logger
    logger.addHandler(file_handler)
    return logger


def touch_file(filepath: Union[Path, str], columns: str) -> None:
    """
    Create an empty file if it does not exist.
    Args:
        filepath (Union[Path, str]): The file path.
        columns (str): The column names.
    """
    # Remove "%(", ")s" from the columns
    columns = columns.replace("%(", "").replace(")s", "")
    print(columns)

    # Create the directory if it does not exist
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    # Create the file if it does not exist
    if not Path(filepath).exists():
        Path(filepath).touch()
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(columns + "\n")


if __name__ == "__main__":
    touch_file(
        "logs/test.log", "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
    )
