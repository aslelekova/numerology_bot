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

    unique_id = str(uuid4())
    link = f"https://yourbot.com/share/{unique_id}"

    # Сохраняем ссылку в базе данных для отслеживания
    await save_share_link(user_id, unique_id)

    # Отправляем сообщение пользователю с уникальной ссылкой
    await callback_query.message.answer(
        f"Отправьте другу эту ссылку, чтобы получить дополнительный вопрос: {link}"
    )

    # Удаляем оригинальное сообщение
    await callback_query.answer()


@app.get("/share/{unique_id}")
async def process_share_link(unique_id: str, request: Request):
    user_id = await get_user_by_share_link(unique_id)

    if user_id:
        # Добавляем дополнительный вопрос первому пользователю
        await increment_user_questions(user_id, 1)

        # Отправляем первому пользователю уведомление
        await bot.send_message(
            user_id,
            "Ваш друг перешел по ссылке! Теперь у вас доступен один дополнительный вопрос. "
            "Нажмите на кнопку ниже, чтобы задать вопрос.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_free_question")]
            ])
        )

    return PlainTextResponse("OK")
