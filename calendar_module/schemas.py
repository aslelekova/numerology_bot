# calendar_module/schemas.py

from enum import Enum

from aiogram.filters.callback_data import CallbackData


class DialogCalAct(str, Enum):
    ignore = "IGNORE"
    start = "START"
    set_y = "SET-YEAR"
    set_m = "SET-MONTH"
    prev_y = "PREV-YEARS"
    next_y = "NEXT-YEARS"
    day = "DAY"
    select_date = "SELECT-DATE"
    matrix = "MATRIX"
    numerology = "NUMEROLOGY"


def highlight(text: str) -> str:
    """
    Wraps the given text in asterisks for markdown-style highlighting.

    :param text: The text to be highlighted.
    :return: The highlighted text wrapped in asterisks.
    """
    return f"*{text}*"


def superscript(text: str) -> str:
    """
    Wraps the given text in superscript symbols for superscript-style formatting.

    :param text: The text to be formatted as superscript.
    :return: The text wrapped in superscript symbols.
    """
    return f"⁺{text}⁺"


class CalendarLabels:

    def __init__(self) -> None:
        self.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.days_of_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        self.today_caption = "Today"


class DialogCalendarCallback(CallbackData, prefix="dialog_calendar"):
    act: DialogCalAct
    year: int
    month: int
    day: int

    @classmethod
    def filter(cls, act: DialogCalAct = None, year: int = None, month: int = None, day: int = None):
        return (
            (act is None or cls.act == act) and
            (year is None or cls.year == year) and
            (month is None or cls.month == month) and
            (day is None or cls.day == day)
        )