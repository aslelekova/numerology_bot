# handlers/matrix_handler.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from states import Form
from handlers.user_input_handler import prompt_for_name

router = Router()


@router.callback_query(F.data == "matrix")
async def handle_matrix(call: CallbackQuery, state: FSMContext):
    """
    Handles the callback query for the "matrix" button, prompting the user to enter their name.

    :param call: The callback query object containing information about the callback event.
    :param state: The FSM (Finite State Machine) context to manage the state of the conversation.
    :return: None
    """
    message_text = (
        "✍️ Введите ваше имя:"
    )
    await prompt_for_name(call, state, message_text, Form.waiting_for_name)
