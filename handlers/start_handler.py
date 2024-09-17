# handlers/start_handler.py
import sqlite3
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.handlers import callback_query

from keyboards.main_menu_keyboard import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    connect = sqlite3. connect( 'users.db')
    cursor = connect. cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
                   id INTEGER
                   )""")
    connect.commit()   
    people_id = message. chat.id
    cursor.execute(f"SELECT id FROM login_id WHERE id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        user_id = [message.chat.id]
        cursor.execute("INSERT INTO login_id VALUES(?);", user_id)
        connect.commit()
    
    user_data = await state.get_data()

    user_name = user_data.get("user_name") or message.from_user.first_name

    await state.clear()

    await message.answer(f"Добрый день, {user_name}!\n\nМы рады помочь вам с расчетом матрицы судьбы, нумерологии, "
                         "совместимости, карьерного успеха, богатства и других вопросов.\n\n<b>После каждого расчета вы"
                         "сможете задать любой вопрос.</b> С чего начнем?", reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def handle_help(message: types.Message):
    """
    Handle the /help command to provide information about available commands and how to use the bot.

    :param message: The message object.
    :return: None
    """
    await message.answer(text=(
        "🔮Этот бот предназначен для того, чтобы помочь вам узнать больше о нумерологии и матрице судьбы. "
        "С его помощью вы можете исследовать, как числа влияют на вашу жизнь, и получить полезные советы и "
        "прогнозы.\n\n"
        "🔹 <b>Доступные команды:</b>\n\n"
        "/start - Начать взаимодействие с ботом. Отправляет приветственное сообщение и предлагает начать "
        "работу.\n\n"
        "/help - Получить информацию о доступных командах и узнать, как пользоваться ботом.\n\n"
    )
    )