from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.main_menu_keyboard import main_menu_keyboard
from services.gpt_service import client
from services.question_service import generate_question_response, generate_suggestions
from states import QuestionState

router = Router()


@router.callback_query(lambda callback: callback.data == "ask_free_question")
async def ask_free_question_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("question_asked", False):
        await callback_query.message.answer("Упс, похоже у вас закончились бесплатные вопросы...")
    else:
        await callback_query.message.answer("Отлично! Теперь вы можете задать свой вопрос (Например: 💕 Как улучшить "
                                            "мои отношения с партнером?)\n\n⚡️ У вас есть 1 бесплатный вопрос")
        await state.set_state(QuestionState.waiting_for_question)


@router.message(StateFilter(QuestionState.waiting_for_question))
async def process_question(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("question_asked", False):
        await message.answer("Упс, похоже у вас закончились бесплатные вопросы...")
        return

    generating_message = await message.answer("⏳")

    user_name = user_data.get('user_name', 'Пользователь')
    birth_date = user_data.get('user_date', 'неизвестна')
    question = message.text  # Используем текст сообщения как вопрос


    response_text = await generate_question_response(question, user_name, birth_date)

    await generating_message.delete()

    await message.answer(response_text)

    # Генерируем предложения на основе заданного вопроса
    suggestions_text = await generate_suggestions(message.text, client)

    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить полный доступ", callback_data="get_full_access")],
        [InlineKeyboardButton(text="Задать еще один вопрос (поделиться с другом)", callback_data="share_and_ask")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
    ])

    suggestion_message_text = (
        f"💫 Задавайте еще больше вопросов своему ассистенту! Вот примеры вопросов, которые могут вас "
        f"заинтересовать:\n\n{suggestions_text}\n\n"
        f"ПОДЕЛИТЕСЬ с другом и получите возможность задать еще один бесплатный вопрос, или ПОЛУЧИТЕ ПОЛНЫЙ ДОСТУП к "
        f"боту, чтобы задавать неограниченное количество вопросов и делать любые расклады! 😍"
    )

    suggestion_message = await message.answer(suggestion_message_text, reply_markup=inline_keyboard)

    previous_message_ids = user_data.get("previous_message_ids", [])
    previous_message_ids.append(suggestion_message.message_id)
    await state.update_data(previous_message_ids=previous_message_ids)
    await state.update_data(question_asked=True)


@router.callback_query(lambda callback: callback.data == "main_menu")
async def main_menu_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_name = callback_query.from_user.first_name

    previous_message_ids = user_data.get("previous_message_ids", [])

    for message_id in previous_message_ids:
        try:
            await callback_query.message.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=message_id
            )
        except Exception as e:
            if "message to delete not found" not in str(e):
                print(f"Error deleting message with ID {message_id}: {e}")

    await state.clear()
    await state.update_data(question_asked=False)

    await callback_query.message.answer(
        f"Добрый день, {user_name}!\n\nМы рады помочь вам с расчетом матрицы судьбы, "
        "нумерологии, совместимости, карьерного успеха, богатства и других вопросов.\n\n"
        "<b>После каждого расчета вы сможете задать любой вопрос.</b> С чего начнем?",
        reply_markup=main_menu_keyboard()
    )

