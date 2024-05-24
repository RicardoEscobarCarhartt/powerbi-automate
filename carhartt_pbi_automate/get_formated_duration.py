"""This module contains the function to get the formatted duration."""
import datetime
from typing import Union


def get_formated_duration(duration: Union[datetime.timedelta, int]) -> str:
    """Returns the formatted duration.
    Args:
        duration (Union[datetime.timedelta, int]): The duration in seconds or a
        timedelta object.
    Returns:
        str: The formatted duration as hours:minutes:seconds."""
    # if the duration is an integer, convert it to a timedelta object
    if isinstance(duration, int):
        duration = datetime.timedelta(seconds=duration)

    # get the hours, minutes, and seconds
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
