# services/message_service.py

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


async def send_message_with_keyboard(message: Message, text: str, keyboard: InlineKeyboardMarkup):
    return await message.answer(text, reply_markup=keyboard)
