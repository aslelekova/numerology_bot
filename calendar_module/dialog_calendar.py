# calendar_module/dialog_calendar.py

import calendar
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from .schemas import DialogCalendarCallback, DialogCalAct, highlight, superscript
from .calendar_utils import GenericCalendar


class DialogCalendar(GenericCalendar):
    ignore_callback = DialogCalendarCallback(act=DialogCalAct.ignore, year=0, month=0, day=0).pack()

    async def _get_month_kb(self, year: int):
        """
        Generates an inline keyboard for month selection of a given year.

        :param year: The year for which the month selection keyboard is generated.
        :return: An inline keyboard markup for selecting months of the specified year.
        :rtype: InlineKeyboardMarkup
        """
        today = datetime.now()
        now_month, now_year = today.month, today.year

        kb = []

        years_row = [
            InlineKeyboardButton(
                text=str(year) if year != today.year else highlight(year),
                callback_data=DialogCalendarCallback(act=DialogCalAct.start, year=year, month=-1, day=-1).pack()
            )
        ]
        kb.append(years_row)

        month_buttons = []
        for month in range(1, 13):
            month_buttons.append(
                InlineKeyboardButton(
                    text=self._highlight_month(year, month, now_year, now_month),
                    callback_data=DialogCalendarCallback(
                        act=DialogCalAct.set_m, year=year, month=month, day=-1
                    ).pack()
                )
            )

        # Arrange buttons in a 3x3 grid (first 9 months).
        for i in range(0, 9, 3):
            kb.append(month_buttons[i:i + 3])

        # Add the last row with remaining 3 months.
        kb.append(month_buttons[9:])

        return InlineKeyboardMarkup(inline_keyboard=kb)

    async def _get_days_kb(self, year: int, month: int, selected_day: int = None):
        """
        Creates a keyboard with buttons for selecting days in a calendar for a given month and year.

        :param year: The year for which the calendar is created.
        :param month: The month for which the calendar is created.
        :param selected_day: Optional. If provided, adds a button to select this date.
        :return: An `InlineKeyboardMarkup` object with the keyboard for selecting days.
        """
        today = datetime.now()
        now_weekday = self._labels.days_of_week[today.weekday()]
        now_month, now_year, now_day = today.month, today.year, today.day

        kb = []
        nav_row = [
            InlineKeyboardButton(
                text=str(year) if year != now_year else highlight(year),
                callback_data=DialogCalendarCallback(act=DialogCalAct.start, year=year, month=-1, day=-1).pack()
            ),
            InlineKeyboardButton(
                text=self._highlight_month(year, month, now_year, now_month),
                callback_data=DialogCalendarCallback(act=DialogCalAct.set_y, year=year, month=-1, day=-1).pack()
            )
        ]
        kb.append(nav_row)

        week_days_labels_row = [
            InlineKeyboardButton(
                text=self._highlight_weekday(weekday, year, month, now_year, now_month, now_weekday),
                callback_data=self.ignore_callback
            )
            for weekday in self._labels.days_of_week
        ]
        kb.append(week_days_labels_row)

        month_calendar = calendar.monthcalendar(year, month)

        for week in month_calendar:
            days_row = [
                InlineKeyboardButton(
                    text=self._highlight_day(day, year, month, now_year, now_month, now_day,
                                             selected_day) if day != 0 else " ",
                    callback_data=DialogCalendarCallback(act=DialogCalAct.day, year=year, month=month,
                                                         day=day).pack() if day != 0 else self.ignore_callback
                )
                for day in week
            ]
            kb.append(days_row)

        if selected_day:
            select_date_button = InlineKeyboardButton(
                text=f"Выбрать {selected_day:02d}.{month:02d}.{year} →",
                callback_data=DialogCalendarCallback(act=DialogCalAct.select_date, year=year, month=month,
                                                     day=selected_day).pack()
            )
            kb.append([select_date_button])

        return InlineKeyboardMarkup(inline_keyboard=kb)

    def _highlight_month(self, year, month, now_year, now_month):
        """
        Highlights the current month in the list of months.

        :return: The name of the month, highlighted if it is the current month.
        :rtype: str
        """
        month_str = self._labels.months[month - 1]
        if now_month == month and now_year == year:
            return f"*{month_str}*"
        return month_str

    def _highlight_weekday(self, weekday, year, month, now_year, now_month, now_weekday):
        """
        Highlights the current weekday if it matches the provided weekday.

        :return: The weekday name, highlighted if it matches the current weekday.
        :rtype: str
        """
        if now_month == month and now_year == year and now_weekday == weekday:
            return highlight(weekday)
        return weekday

    def _highlight_day(self, day, year, month, now_year, now_month, now_day, selected_day):
        """
        Highlights the current day if it matches the provided day, and adds a checkmark if the day is selected.

        :return: The day string, highlighted if it matches the current day or is selected.
        :rtype: str
        """
        day_string = self._format_day_string(day, year, month)
        if selected_day == day:
            day_string += " ✓"
        if now_month == month and now_year == year and now_day == day:
            return highlight(day_string)
        return day_string

    def _format_day_string(self, day, year, month):
        """
        Formats the day string considering min and max date constraints.

        :return: The day string, with superscript formatting if outside the allowed date range.
        :rtype: str
        """
        date_to_check = datetime(year, month, day)
        if self.min_date and date_to_check < self.min_date:
            return superscript(str(day))
        elif self.max_date and date_to_check > self.max_date:
            return superscript(str(day))
        return str(day)

    async def start_calendar(
            self,
            year: int = datetime.now().year,
            month: int = None
    ) -> InlineKeyboardMarkup:
        """
        Starts a calendar for a given year and optionally a specific month.

        :param year: The year for which the calendar is created. Defaults to the current year.
        :param month: Optional. The month for which the calendar is created. If not provided, the year view is displayed.
        :return: An `InlineKeyboardMarkup` object with the keyboard for the calendar.
        """
        if month:
            return await self._get_days_kb(year, month)

        return await self._get_year_kb(year)

    async def _get_year_kb(self, current_year: int) -> InlineKeyboardMarkup:
        """
        Generates a keyboard for selecting years within a range around the given year.

        :param current_year: The reference year for generating the calendar keyboard.
        :return: An `InlineKeyboardMarkup` object with the keyboard for year selection.
        """
        kb = []
        today = datetime.now()
        now_year = today.year

        year_buttons = [
            InlineKeyboardButton(
                text=str(year) if year != now_year else highlight(year),
                callback_data=DialogCalendarCallback(act=DialogCalAct.set_y, year=year, month=-1, day=-1).pack()
            )
            for year in range(current_year - 7, current_year + 8)
        ]

        for i in range(0, 15, 3):
            kb.append(year_buttons[i:i + 3])

        nav_row = [
            InlineKeyboardButton(
                text='←',
                callback_data=DialogCalendarCallback(act=DialogCalAct.prev_y, year=current_year, month=-1,
                                                     day=-1).pack()
            ),
            InlineKeyboardButton(
                text='→',
                callback_data=DialogCalendarCallback(act=DialogCalAct.next_y, year=current_year, month=-1,
                                                     day=-1).pack()
            )
        ]
        kb.append(nav_row)

        return InlineKeyboardMarkup(inline_keyboard=kb)

    async def process_selection(self, query: CallbackQuery, data: DialogCalendarCallback) -> tuple:
        """
        Handles user selection from the calendar interface and updates the message accordingly.

        :param query: The callback query object from the user interaction.
        :param data: The callback data containing action and parameters.
        :return: A tuple indicating success and the selected date or None.
        :rtype: tuple
        """
        return_data = (False, None)
        if data.act == DialogCalAct.ignore:
            await query.answer(cache_time=60)
        elif data.act == DialogCalAct.set_y:
            await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(int(data.year)))
        elif data.act == DialogCalAct.prev_y:
            new_year = int(data.year) - 5
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(year=new_year))
        elif data.act == DialogCalAct.next_y:
            new_year = int(data.year) + 5
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(year=new_year))
        elif data.act == DialogCalAct.set_m:
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(int(data.year), int(data.month)))
        elif data.act == DialogCalAct.start:
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(int(data.year)))
        elif data.act == DialogCalAct.day:
            await query.message.edit_reply_markup(
                reply_markup=await self._get_days_kb(int(data.year), int(data.month), selected_day=int(data.day))
            )
        elif data.act == DialogCalAct.select_date:
            return_data = (True, datetime(int(data.year), int(data.month), int(data.day)))
        return return_data
