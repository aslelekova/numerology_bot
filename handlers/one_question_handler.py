# handlers/one_question_handler.py

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.start_handler import cmd_start
from services.question_service import generate_response, generate_suggestions
from services.message_service import delete_previous_messages
from states import QuestionState

router = Router()


@router.callback_query(lambda callback: callback.data == "ask_free_question")
async def ask_free_question_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Проверка, был ли уже задан вопрос
    user_data = await state.get_data()
    if user_data.get("question_asked", False):
        await callback_query.message.answer("Упс, похоже у вас закончились бесплатные вопросы...")
        return

    await callback_query.message.answer(
        "Отлично! Теперь вы можете задать свой вопрос (Например: 💕 Как улучшить мои отношения с партнером?)\n\n"
        "⚡️ У вас есть 1 бесплатный вопрос"
    )
    await state.set_state(QuestionState.waiting_for_question)


@router.message(StateFilter(QuestionState.waiting_for_question))
async def process_question(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("question_asked", False):
        await message.answer("Упс, похоже у вас закончились бесплатные вопросы...")
        return

    prompt = f"У вас есть пользователь с именем {user_data['user_name']}, дата рождения {user_data['user_date']}. Пользователь задал следующий вопрос: '{message.text}'."
    response_text = await generate_response(prompt)

    await message.answer(response_text)
    suggestions_text = await generate_suggestions(message.text)
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить полный доступ", callback_data="get_full_access")],
        [InlineKeyboardButton(text="Задать еще один вопрос (поделиться с другом)", callback_data="share_and_ask")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
    ])
    suggestion_message = await message.answer(f"💫 Вот примеры вопросов:\n\n{suggestions_text}",
                                              reply_markup=inline_keyboard)

    await state.update_data(previous_message_ids=[suggestion_message.message_id])
    await state.update_data(question_asked=True)


@router.callback_query(lambda callback: callback.data == "main_menu")
async def main_menu_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await delete_previous_messages(callback_query.message.chat.id, user_data.get("previous_message_ids", []),
                                   callback_query.message.bot)
    await cmd_start(callback_query.message)
