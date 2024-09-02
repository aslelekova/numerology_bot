# calendar_module/calendar_utils.py
import calendar
import locale
from aiogram.types import User
from datetime import datetime
from .schemas import CalendarLabels


async def get_user_locale(from_user: User) -> str:
    """
    Extracts and returns the locale string from a user object.

    :param from_user: The `User` object containing the `language_code`.
    :type from_user: User
    :return: The simplified locale string.
    :rtype: str
    """
    loc = from_user.language_code
    return locale.locale_alias[loc].split(".")[0]


class GenericCalendar:

    def __init__(
            self,
            locale: str = None,
            today_btn: str = None,
            show_alerts: bool = False
    ) -> None:
        """
        A calendar class with customizable labels and alert options.

        :param locale: Optional locale for displaying days and months.
        :param today_btn: Optional text for the "Today" button.
        :param show_alerts: Whether to show alerts; default is False.
        """
        self._labels = CalendarLabels()
        if locale:
            with calendar.different_locale(locale):
                self._labels.days_of_week = list(calendar.day_abbr)
                self._labels.months = calendar.month_abbr[1:]

        if today_btn:
            self._labels.today_caption = today_btn

        self.min_date = None
        self.max_date = None
        self.show_alerts = show_alerts

    def set_dates_range(self, min_date: datetime, max_date: datetime):
        """
        Sets the range of dates for the calendar.

        :param min_date: The minimum date in the range.
        :param max_date: The maximum date in the range.
        """
        self.min_date = min_date
        self.max_date = max_date

    async def process_day_select(self, data, query):
        """
        Processes a selected date and checks if it falls within the allowed range.

        :param data: Data containing the selected date (year, month, day).
        :param query: The query object used to send responses.
        :return: A tuple (bool, datetime or None). Returns True and the date if valid,
                     otherwise False and None.
        """
        date = datetime(int(data.year), int(data.month), int(data.day))
        if self.min_date and self.min_date > date:
            await query.answer(
                f'The date must be later than {self.min_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        elif self.max_date and self.max_date < date:
            await query.answer(
                f'The date must be before {self.max_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        await query.message.delete_reply_markup()
        return True, date
