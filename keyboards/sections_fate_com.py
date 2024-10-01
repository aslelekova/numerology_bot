# keyboards/sections_fate_matrix.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def create_sections_keyboard_com() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Для чего пара встретилась ✅", callback_data="com_meeting_purpose")],
            [InlineKeyboardButton(text="Как пара выглядит для других ✅", callback_data="com_appearance")],
            [InlineKeyboardButton(text="Общая атмосфера внутри пары 🔐", callback_data="com_atmosphere")],
            [InlineKeyboardButton(text="Что укрепляет союз 🔐", callback_data="com_strengthen_union")],
            [InlineKeyboardButton(text="Финансы 🔐", callback_data="com_finances")],
            [InlineKeyboardButton(text="Желания и цели 🔐", callback_data="com_wishes_goals")],
            [InlineKeyboardButton(text="Задачи пары 🔐", callback_data="com_tasks")],
            [InlineKeyboardButton(text="Трудности и недопонимания 🔐", callback_data="com_difficulties")],
        ]
    )



def create_full_sections_keyboard_com() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Для чего пара встретилась", callback_data="com_meeting_purpose")],
            [InlineKeyboardButton(text="Как пара выглядит для других", callback_data="com_appearance")],
            [InlineKeyboardButton(text="Общая атмосфера внутри пары", callback_data="com_atmosphere")],
            [InlineKeyboardButton(text="Что укрепляет союз", callback_data="com_strengthen_union")],
            [InlineKeyboardButton(text="Финансы", callback_data="com_finances")],
            [InlineKeyboardButton(text="Желания и цели", callback_data="com_wishes_goals")],
            [InlineKeyboardButton(text="Задачи пары", callback_data="com_tasks")],
            [InlineKeyboardButton(text="Трудности и недопонимания", callback_data="com_difficulties")],
        ]
    )

