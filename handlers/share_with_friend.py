import uuid

from aiogram import types
from aiogram.fsm.context import FSMContext
from fastapi import FastAPI, Request, Depends
from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from services.db_service import update_questions_left
from services.message_service import save_message_id

router = Router()
app = FastAPI()


def generate_share_link(user_id: int) -> str:
    unique_token = str(uuid.uuid4())
    return f"https://t.me/MakeMyMatrix_Bot?user_id={user_id}&token={unique_token}"


@router.callback_query(lambda callback: callback.data == "share_and_ask")
async def share_and_ask_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    share_link = generate_share_link(user_id)

    await callback_query.message.answer(
        f"Поделитесь этой ссылкой с другом, чтобы они могли задать вам вопрос: {share_link}"
    )

async def get_fsm_context(state: FSMContext = Depends()):
    return state


@app.get("/share")
async def share_redirect(user_id: int, token: str, callback_query: CallbackQuery, state: FSMContext = Depends(get_fsm_context)):
    # Логика проверки токена здесь (если нужно)

    # Обновляем количество доступных вопросов
    await update_questions_left(user_id, 1)

    # Отправляем уведомление пользователю, который поделился ссылкой
    await notify_user(callback_query, state)

    return {"message": "Спасибо, ваш друг теперь может задать дополнительный вопрос!"}


async def notify_user(callback_query: CallbackQuery, state: FSMContext):
    message_text = await callback_query.message.answer(
        f"Ваш друг перешел по ссылке и теперь может задать дополнительный вопрос!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_free_question")]
        ]),
    )

    await state.update_data(message_text_id=message_text.message_id)
    await save_message_id(state, message_text.message_id)
