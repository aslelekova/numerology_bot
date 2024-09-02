# handlers/numerology_handler.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.user_input_handler import prompt_for_name
from states import Form

router = Router()


@router.callback_query(F.data == "numerology")
async def handle_numerology(call: CallbackQuery, state: FSMContext):
    message_text = (
        "✨ Хотите узнать, какие секреты хранят числа вашего рождения? Откройте дверь в мир нумерологии и узнайте, "
        "что вас ждет впереди!Введите вашу дату рождения и имя, и получите ключ к пониманию своей судьбы.\n\n"
        "Пожалуйста, введите ваше имя 👇"
    )
    await prompt_for_name(call, state, message_text, Form.waiting_for_name)
