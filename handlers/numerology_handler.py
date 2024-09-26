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
        "✍️ Введите ваше ФИО:"
    )
    await prompt_for_name(call, state, message_text, Form.waiting_for_name)
