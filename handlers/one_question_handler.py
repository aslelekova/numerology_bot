# handlers/one_question_handler.py
from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.main_menu_keyboard import main_menu_keyboard
from services.db_service import get_questions_left, get_subscription_details, update_questions_left
from services.message_service import save_message_id
from services.question_service import generate_question_response, generate_suggestions
from states import QuestionState

router = Router()

@router.callback_query(lambda callback: callback.data == "ask_free_question")
async def ask_free_question_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    questions_left = await get_questions_left(user_id)

    data = await state.get_data()
    previous_warning_message_id = data.get("previous_warning_message_id")

    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"Ошибка при удалении сообщения с кнопкой: {e}")


    if previous_warning_message_id:
        try:
            await callback_query.message.bot.delete_message(chat_id=callback_query.message.chat.id,
                                                            message_id=previous_warning_message_id)
        except Exception as e:
            print(f"Ошибка при удалении предыдущего предупреждающего сообщения: {e}")

    if questions_left <= 0:
        try:
            message = await callback_query.message.answer("Упс, похоже у вас закончились бесплатные вопросы...")
            await save_message_id(state, message.message_id)
        except Exception as e:
            # Обрабатываем все остальные исключения
            print(f"Произошла ошибка: {e}")
    else:
        message = await callback_query.message.answer(
            f"Отлично! Теперь вы можете задать свой вопрос (Например: 💕 Как улучшить мои отношения с партнером?)\n\nУ вас доступно:\n ⚡️ {questions_left} ответа на любые вопросы"
        )
        await save_message_id(state, message.message_id)
        await state.set_state(QuestionState.waiting_for_question)

@router.message(StateFilter(QuestionState.waiting_for_question))
async def process_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    subscription_details = await get_subscription_details(user_id)
    subscription_active = subscription_details["subscription_active"]
    questions_left = subscription_details["questions_left"]
    if questions_left <= 0:
        await message.delete()
        warning_message = await message.answer("Упс, похоже у вас закончились бесплатные вопросы...")
        await save_message_id(state, warning_message.message_id)
        return

    generating_message = await message.answer("Подождите минутку, мы готовим для вас ответ ⏳")
    await save_message_id(state, generating_message.message_id)

    user_data = await state.get_data()
    user_name = user_data.get('user_name', 'Пользователь')
    birth_date = user_data.get('user_date', 'неизвестна')
    question = message.text
    await save_message_id(state, message.message_id)

    response_text = await generate_question_response(question, user_name, birth_date, state)

    if response_text is not None:
        response_text = response_text.replace("#", "").replace("*", "")

    await generating_message.delete()

    response_message = await message.answer(response_text)
    await save_message_id(state, response_message.message_id)

    new_questions_left = questions_left - 1
    await update_questions_left(user_id, new_questions_left)

    suggestions_text = await generate_suggestions(message.text)

    if subscription_active and new_questions_left > 0:
        three_functions = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться к разделам 👈", callback_data="go_back_to_categories")],
            [InlineKeyboardButton(text="Получить полный доступ", callback_data="get_full_access")],
            [InlineKeyboardButton(text="Задать еще один вопрос", callback_data="ask_free_question")],
        ])
        suggestion_message_text = (
            f"💫 Задавайте еще больше вопросов своему ассистенту! Вот примеры вопросов, которые могут вас "
            f"заинтересовать:\n\n{suggestions_text}\n\n"
            f"ПОДЕЛИТЕСЬ с другом и получите возможность задать еще один бесплатный вопрос, или ПОЛУЧИТЕ ПОЛНЫЙ ДОСТУП к "
            f"боту, чтобы задавать неограниченное количество вопросов и делать любые расклады! 😍"
        )
    else:
        three_functions = InlineKeyboardMarkup(inline_keyboard=[
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

    suggestion_message = await message.answer(suggestion_message_text, reply_markup=three_functions)
    await save_message_id(state, suggestion_message.message_id)

@router.callback_query(lambda callback: callback.data == "main_menu")
async def main_menu_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_name = callback_query.from_user.first_name

    all_message_ids = user_data.get("all_message_ids", [])
    for message_id in all_message_ids:
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

    main_menu_message = await callback_query.message.answer(
        f"Добрый день, {user_name}!\n\nМы рады помочь вам с расчетом матрицы судьбы, "
        "нумерологии, совместимости, карьерного успеха, богатства и других вопросов.\n\n"
        "<b>После каждого расчета вы сможете задать любой вопрос.</b> С чего начнем?",
        reply_markup=main_menu_keyboard()
    )
    await save_message_id(state, main_menu_message.message_id)

