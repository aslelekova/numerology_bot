from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from services.message_service import save_message_id

router = Router()



@router.callback_query(lambda callback: callback.data == "share_and_ask")
async def share_and_ask_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    link = f"https://t.me/MakeMyMatrix_Bot?start={user_id}"

    link_message = await callback_query.message.answer(
        f"Поделитесь этой ссылкой с другом и получите бесплатный вопрос:\n{link}\n\nКак только друг перейдет по ссылке у вас будет доступен вопрос"
    )
    await state.update_data(link_message_id=link_message.message_id)
    await save_message_id(state, link_message.message_id)

    await callback_query.answer()
