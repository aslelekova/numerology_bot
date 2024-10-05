import aiosqlite
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from keyboards.main_menu_keyboard import main_menu_keyboard
from services.db_service import Database

db = Database()

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await db.setup()

    user_id = message.from_user.id
    start_command = message.text

    # Проверка, существует ли пользователь в базе данных
    if not await db.user_exists(user_id):
        # Извлечение реферального ID
        referrer_id = str(start_command[7:])  # Получаем реферальный ID из команды

        if referrer_id:  # Проверяем, что referrer_id не пустой
            if referrer_id != str(
                    user_id):  # Проверяем, что пользователь не пытается зарегистрироваться по своей ссылке
                await db.add_user(user_id, referrer_id)  # Добавляем пользователя с реферальным ID
                try:
                    await message.answer(f"По вашей ссылке зарегистрировался новый пользователь!")
                except Exception as e:
                    print(f"Ошибка при отправке сообщения: {e}")
            else:
                await message.answer("Нельзя регистрироваться по собственной реферальной ссылке!")
        else:
            await db.add_user(user_id)  # Если нет реферального ID, просто добавляем пользователя

    # Получаем имя пользователя
    user_data = await state.get_data()
    user_name = user_data.get("user_name") or message.from_user.first_name

    # Очищаем состояние FSM
    await state.clear()

    # Отправляем приветственное сообщение
    await message.answer(
        f"Добрый день, {user_name}!\n\nМы рады помочь вам с расчетом матрицы судьбы, нумерологии, "
        "совместимости, карьерного успеха, богатства и других вопросов.\n\n<b>После каждого расчета вы "
        "сможете задать любой вопрос.</b> С чего начнем?",
        reply_markup=main_menu_keyboard()  # Предполагается, что у вас есть функция main_menu_keyboard()
    )