# keyboards/back_to_menu.py

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu"))
    return kb.as_markup()


def create_back_button():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться к разделам 👈", callback_data="go_back_to_categories")]
    ])
    return keyboard

