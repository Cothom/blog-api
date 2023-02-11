"""Utility functions"""

from datetime import datetime


def iso_string_to_datetime(iso_string: str | None) -> datetime:
    """Convert date from ISO format to datetime object

    Args:
        iso_string (str | None): String to convert

    Returns:
        datetime: Datetime object. It corresponds to now if an error occured.
    """
    date: datetime = datetime.now()
    if iso_string:
        try:
            date = datetime.fromisoformat(iso_string)
        except ValueError:
            # If it cannot be parsed as isoformat, get current date
            pass
    return date


def datetime_to_iso_string(date: datetime) -> str:
    """Convert datetime object into an ISO string

    Args:
        date (datetime): Datetime object to convert

    Returns:
        str: ISO-formatted string
    """
    return date.isoformat()
