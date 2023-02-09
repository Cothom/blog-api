from datetime import datetime


def iso_string_to_datetime(iso_string: str | None) -> datetime:
    date: datetime = datetime.now()
    if iso_string:
        try:
            date = datetime.fromisoformat(iso_string)
        except ValueError:
            # If it cannot be parsed as isoformat, get current date
            pass
    return date


def datetime_to_iso_string(date: datetime) -> str:
    return date.isoformat()
