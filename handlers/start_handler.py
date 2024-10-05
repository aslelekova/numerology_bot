import aiosqlite
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.main_menu_keyboard import main_menu_keyboard
from services.db_service import setup_db, user_exists, add_user, get_questions_left, update_questions_left
from services.message_service import save_message_id

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await setup_db()
    user_id = message.from_user.id
    start_command = message.text

    if not await user_exists(user_id):
        referrer_id = str(start_command[7:])

        if referrer_id:
            if referrer_id != str(user_id):
                await add_user(user_id, referrer_id)

                data = await state.get_data()
                link_message_id = data.get("link_message_id")

                if link_message_id:
                    try:
                        await message.bot.delete_message(chat_id=message.chat.id, message_id=link_message_id)
                    except Exception as e:
                        print(f"Ошибка при удалении сообщения: {e}")

                try:
                    question_prompt_message = await message.bot.send_message(referrer_id,
                        f"По вашей ссылке зарегистрировался новый пользователь! Вы можете задать бесплатный вопрос!",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_free_question")]
                        ]),
                        parse_mode="HTML"
                    )
                    await state.update_data(question_prompt_message_id=question_prompt_message.message_id)
                    await save_message_id(state, question_prompt_message.message_id)

                    questions_left = await get_questions_left(int(referrer_id))
                    await update_questions_left(int(referrer_id), questions_left + 1)
                except Exception as e:


                    print(f"Ошибка при отправке сообщения рефереру: {e}")
            else:
                await message.answer("Нельзя регистрироваться по собственной реферальной ссылке!")
        else:
            await add_user(user_id)

    user_data = await state.get_data()
    user_name = user_data.get("user_name") or message.from_user.first_name


    await message.answer(
        f"Добрый день, {user_name}!\n\nМы рады помочь вам с расчетом матрицы судьбы, нумерологии, "
        "совместимости, карьерного успеха, богатства и других вопросов.\n\n<b>После каждого расчета вы "
        "сможете задать любой вопрос.</b> С чего начнем?",
        reply_markup=main_menu_keyboard()
    )

