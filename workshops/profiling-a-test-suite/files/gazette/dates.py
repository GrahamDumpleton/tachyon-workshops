"""Dates as the gazette prints them."""

from datetime import date

MONTHS = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def printed(text):
    """Turn 2026-09-23 into Wednesday 23 September 2026."""
    day = date.fromisoformat(text)
    return f"{DAYS[day.weekday()]} {day.day} {MONTHS[day.month - 1]} {day.year}"


def issue(text):
    """The number of the issue an article appeared in, one for each day of the year."""
    day = date.fromisoformat(text)
    return day.timetuple().tm_yday
