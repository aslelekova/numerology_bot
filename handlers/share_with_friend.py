from uuid import uuid4

from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOT_TOKEN
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

router = Router()



@router.callback_query(lambda callback: callback.data == "share_and_ask")
async def share_and_ask_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    link = f"https://t.me/MakeMyMatrix_Bot?start={user_id}"

    await callback_query.message.answer(
        f"Отправьте другу эту ссылку, чтобы задать еще один вопрос  :\n{link}"
    )

    # Удаляем оригинальное сообщение
    await callback_query.answer()
