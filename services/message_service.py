# services/message_service.py
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.types import CallbackQuery
from aiogram import types

from aiogram.types import InlineKeyboardMarkup


async def delete_message(bot, chat_id, message_id):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        if "message to delete not found" not in str(e):
            print(f"Error deleting message: {e}")


async def delete_messages(bot, chat_id: int, message_ids: list[int]):
    for message_id in message_ids:
        if message_id:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                print(f"Ошибка при удалении сообщения {message_id}: {e}")


async def send_initial_messages(bot, chat_id: int, state: FSMContext, section_message: str, question_message: str,
                                sections_keyboard, functions_keyboard):
    first_message = await bot.send_message(chat_id, section_message, reply_markup=sections_keyboard)
    await state.update_data(first_message_id=first_message.message_id)

    question_prompt_message = await bot.send_message(
        chat_id,
        question_message,
        reply_markup=functions_keyboard,
        parse_mode="HTML"
    )
    await state.update_data(question_prompt_message_id=question_prompt_message.message_id)
    await save_message_id(state, question_prompt_message.message_id)


async def notify_subscription_expired(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Упс, похоже у вас закончился тариф, откройте полный доступ к приложению чтобы продолжить расчет 🫶"
    )

    full_access_message = (
        "Получите ответы на все свои вопросы с ПОЛНЫМ доступом к:\n"
        "🔮 Матрице судьбы\n"
        "💸 Нумерологии | Личному успеху | Финансам\n"
        "💕 Совместимости с партнером\n\n"
        "Или задайте любой вопрос нашему персональному ассистенту и получите мгновенный ответ (например: 💕 Как улучшить отношения с партнером?)"
    )

    access_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить полный доступ", callback_data="get_full_access")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ])

    mes = await callback_query.message.answer(
        full_access_message,
        reply_markup=access_keyboard,
        parse_mode="HTML"
    )

    await save_message_id(state, mes.message_id)



async def save_message_id(state: FSMContext, message_id: int):
    data = await state.get_data()
    all_message_ids = data.get("all_message_ids", [])
    all_message_ids.append(message_id)
    await state.update_data(all_message_ids=all_message_ids)
