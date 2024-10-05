import uuid
from fastapi import FastAPI
from aiogram import types
from aiogram import Router

from services.db_service import update_questions_left

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

@app.get("/share")
async def share_redirect(user_id: int, token: str):
    # Логика проверки токена здесь (если нужно)
    await update_questions_left(user_id, 1)
    return {"message": "Спасибо, ваш друг теперь может задать дополнительный вопрос!"}
