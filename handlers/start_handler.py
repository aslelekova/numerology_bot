import aiosqlite
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from keyboards.main_menu_keyboard import main_menu_keyboard

router = Router()
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    async with aiosqlite.connect('users.db') as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS login_id (
                id INTEGER PRIMARY KEY,
                tariff TEXT DEFAULT 'none',
                readings_left INTEGER DEFAULT 0,
                questions_left INTEGER DEFAULT 1, 
                subscription_active BOOLEAN DEFAULT 0
            )
        """)
        await db.commit()

        people_id = message.chat.id
        
        cursor = await db.execute("SELECT id FROM login_id WHERE id = ?", (people_id,))
        data = await cursor.fetchone()

        if data is None:
            await db.execute("INSERT INTO login_id (id) VALUES (?)", (people_id,))
            await db.commit()

    user_data = await state.get_data()
    user_name = user_data.get("user_name") or message.from_user.first_name

    await state.clear()

    await message.answer(
        f"Добрый день, {user_name}!\n\nМы рады помочь вам с расчетом матрицы судьбы, нумерологии, "
        "совместимости, карьерного успеха, богатства и других вопросов.\n\n<b>После каждого расчета вы "
        "сможете задать любой вопрос.</b> С чего начнем?", 
        reply_markup=main_menu_keyboard()
    )
