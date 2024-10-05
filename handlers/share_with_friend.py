from uuid import uuid4

from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext

from services.message_service import save_message_id

router = Router()



@router.callback_query(lambda callback: callback.data == "share_and_ask")
async def share_and_ask_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    link = f"https://t.me/MakeMyMatrix_Bot?start={user_id}"

    link_message = await callback_query.message.answer(
        f"Отправьте другу эту ссылку, чтобы задать еще один вопрос:\n{link}"
    )
    await state.update_data(link_message_id=link_message.message_id)
    await save_message_id(state, link_message.message_id)

    # Удаляем оригинальное сообщение
    await callback_query.answer()
