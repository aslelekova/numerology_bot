# keyboards/sections_fate_matrix.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def create_sections_keyboard_num() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Личность и психика ✅", callback_data="section_num_personality_psychic")],
            [InlineKeyboardButton(text="Чувства и самореализация 🔐", callback_data="section_num_emotions_selfrealization")],
            [InlineKeyboardButton(text="Образование и духовное развитие 🔐", callback_data="section_num_education_spirituality")],
            [InlineKeyboardButton(text="Отношения и ответственность 🔐", callback_data="section_num_relationships_responsibility")],
            [InlineKeyboardButton(text="Опыт и финансовая сфера 🔐", callback_data="section_num_experience_finances")],
            [InlineKeyboardButton(text="Личная сила и трансформация 🔐", callback_data="section_num_personal_power_transformation")],
            [InlineKeyboardButton(text="Психология и внутренний баланс 🔐", callback_data="section_num_psychology_balance")],
            [InlineKeyboardButton(text="Социальная и семейная сфера 🔐", callback_data="section_num_social_family")],
        ]
    )



def create_full_sections_keyboard_num() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Личность и психика", callback_data="section_num_personality_psychic")],
            [InlineKeyboardButton(text="Чувства и самореализация", callback_data="section_num_emotions_selfrealization")],
            [InlineKeyboardButton(text="Образование и духовное развитие", callback_data="section_num_education_spirituality")],
            [InlineKeyboardButton(text="Отношения и ответственность", callback_data="section_num_relationships_responsibility")],
            [InlineKeyboardButton(text="Опыт и финансовая сфера", callback_data="section_num_experience_finances")],
            [InlineKeyboardButton(text="Личная сила и трансформация", callback_data="section_num_personal_power_transformation")],
            [InlineKeyboardButton(text="Психология и внутренний баланс", callback_data="section_num_psychology_balance")],
            [InlineKeyboardButton(text="Социальная и семейная сфера", callback_data="section_num_social_family")],
        ]
    )
