# services/calendar_service.py

from aiogram.filters.callback_data import CallbackData

from calendar_module.calendar_utils import get_user_locale
from calendar_module.dialog_calendar import DialogCalendar
from aiogram.types import CallbackQuery
from calendar_module.schemas import DialogCalendarCallback


async def start_calendar(locale):
    """
    Starts a calendar dialog with localization based on the user's locale.

    :param locale: A string representing the locale used to localize the calendar (e.g., 'en', 'ru').
    :return: An InlineKeyboardMarkup object representing the keyboard for the calendar dialog.
    """
    return await DialogCalendar(locale=locale).start_calendar()


async def process_calendar_selection(callback_query: CallbackQuery, callback_data: CallbackData):
    """
    Processes a calendar selection from a callback query.

    :param callback_query: The callback query object containing details about the user interaction.
    :param callback_data: The callback data extracted from the callback query, including selected date and action.
    :return: A tuple where the first element is a boolean indicating if a date was selected, and the second element is the selected date if applicable.
    """
    locale = await get_user_locale(callback_query.from_user)

    dialog_callback_data = DialogCalendarCallback.parse_obj(callback_data)

    return await DialogCalendar(locale=locale).process_selection(callback_query, dialog_callback_data)