# services/message_service.py
from aiogram.fsm.context import FSMContext

from aiogram import types

from aiogram.types import InlineKeyboardMarkup


async def delete_previous_messages(chat_id: int, message_ids: list, bot):
    for message_id in message_ids:
        try:
            await bot.delete_message(chat_id, message_id)
        except Exception as e:
            if "message to delete not found" not in str(e):
                print(f"Error deleting message with ID {message_id}: {e}")


async def delete_message(bot, chat_id, message_id):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        if "message to delete not found" not in str(e):
            print(f"Error deleting message: {e}")


async def send_message_with_keyboard(message: types.Message, text: str, keyboard: InlineKeyboardMarkup):
    return await message.answer(text, reply_markup=keyboard)


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




