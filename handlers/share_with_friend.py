from uuid import uuid4

from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOT_TOKEN
from services.db_service import save_share_link, get_user_by_share_link, increment_user_questions

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()
router = Router()
bot = Bot(token=BOT_TOKEN)
@router.callback_query(lambda callback: callback.data == "share_and_ask")
async def share_and_ask_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    # Генерация уникального идентификатора
    unique_id = str(uuid4())
    link = f"https://t.me/MakeMyMatrix_Bot?unique_id={unique_id}"

    # Сохранение уникальной ссылки в базе данных
    await save_share_link(user_id, unique_id)

    # Отправка сообщения с уникальной ссылкой
    await callback_query.message.answer(
        f"Отправьте другу эту ссылку, чтобы получить дополнительный вопрос: {link}"
    )

    # Удаляем оригинальное сообщение
    await callback_query.answer()

# Обработчик перехода по уникальной ссылке
@router.message(lambda message: message.text.startswith('https://t.me/MakeMyMatrix_Bot?unique_id='))
async def process_share_link(message: types.Message, state: FSMContext):
    # Извлечение уникального идентификатора из текста сообщения
    unique_id = message.text.split('=')[1]  # Получаем unique_id

    # Получение user_id по уникальной ссылке
    user_id = await get_user_by_share_link(unique_id)

    if user_id:
        # Добавление дополнительного вопроса первому пользователю
        await increment_user_questions(user_id, 1)

        # Отправка уведомления первому пользователю
        await bot.send_message(
            user_id,
            "Ваш друг перешел по ссылке! Теперь у вас доступен один дополнительный вопрос. "
            "Нажмите на кнопку ниже, чтобы задать вопрос.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_free_question")]
            ])
        )

    await message.answer("Вы успешно перешли по ссылке!")
