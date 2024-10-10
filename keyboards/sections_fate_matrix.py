# keyboards/sections_fate_matrix.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def create_sections_keyboard() -> InlineKeyboardMarkup:
    """
    Creates and returns a keyboard with buttons for various sections of the fate matrix.

    The keyboard includes sections that are available for free (marked with ✅) and sections that require full access
    (marked with 🔐).

    :return: An InlineKeyboardMarkup object representing the keyboard with buttons for different sections of the fate
    matrix.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Личные качества ✅", callback_data="section_personal")],
            [InlineKeyboardButton(text="Предназначение ✅", callback_data="section_destiny")],
            [InlineKeyboardButton(text="Детско-родительские отношения ✅",
                                  callback_data="section_family_relationships")],
            [InlineKeyboardButton(text="Таланты ✅", callback_data="section_talents")],
            [InlineKeyboardButton(text="Родовые программы 🔐", callback_data="section_generic_programs")],
            [InlineKeyboardButton(text="Кармический хвост 🔐", callback_data="section_karmic_tail")],
            [InlineKeyboardButton(text="Главный кармический урок 🔐", callback_data="section_karmic_lesson")],
            [InlineKeyboardButton(text="Отношения 🔐", callback_data="section_relationships")],
            [InlineKeyboardButton(text="Деньги 🔐", callback_data="section_money")],
        ]
    )



def create_full_sections_keyboard() -> InlineKeyboardMarkup:
    """
    Creates and returns a keyboard with buttons for various sections of the fate matrix.

    The keyboard includes sections that are available for free (marked with ✅) and sections that require full access
    (marked with 🔐).

    :return: An InlineKeyboardMarkup object representing the keyboard with buttons for different sections of the fate
    matrix.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Личные качества", callback_data="section_personal")],
            [InlineKeyboardButton(text="Предназначение", callback_data="section_destiny")],
            [InlineKeyboardButton(text="Детско-родительские отношения",
                                  callback_data="section_family_relationships")],
            [InlineKeyboardButton(text="Таланты", callback_data="section_talents")],
            [InlineKeyboardButton(text="Родовые программы", callback_data="section_generic_programs")],
            [InlineKeyboardButton(text="Кармический хвост", callback_data="section_karmic_tail")],
            [InlineKeyboardButton(text="Главный кармический урок", callback_data="section_karmic_lesson")],
            [InlineKeyboardButton(text="Отношения", callback_data="section_relationships")],
            [InlineKeyboardButton(text="Деньги", callback_data="section_money")],
        ]
    )



def create_reply_keyboard():
    button = KeyboardButton(text="Главное меню")

    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [button]
        ]
    )
    return keyboard


def functions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Получить полный доступ", callback_data="get_full_access")],
                [InlineKeyboardButton(text="Задать бесплатный вопрос", callback_data="ask_free_question")],
                [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
            ])
            
    

def create_tariff_keyboard(payment_url_1: str, payment_url_2: str, payment_url_3: str, back_callback: str = "back") -> InlineKeyboardMarkup:
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="590 руб", url=payment_url_1)],
            [InlineKeyboardButton(text="790 руб", url=payment_url_2),
             InlineKeyboardButton(text="990 руб", url=payment_url_3)],
            [InlineKeyboardButton(text="Назад", callback_data=back_callback)]
        ]
    )
    
    return keyboard