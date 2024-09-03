# keyboards/main_menu_keyboard.py

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder



def main_menu_keyboard():
    """
    Creates and returns the main menu keyboard with options for different features.

    :return: An InlineKeyboardMarkup object representing the main menu keyboard with buttons for various features.
    """
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔮 Матрица судьбы", callback_data="matrix"))
    kb.row(types.InlineKeyboardButton(text="💸 Нумерология | Личный успех | Финансы", callback_data="numerology"))
    kb.row(types.InlineKeyboardButton(text="💕 Совместимость с человеком", callback_data="compatibility"))
    return kb.as_markup()
