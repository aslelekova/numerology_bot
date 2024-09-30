# handlers/compatibility_handler.py

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states import Form

router = Router()


@router.callback_query(lambda c: c.data == "compatibility")
async def handle_compatibility(call: CallbackQuery, state: FSMContext):
    await call.message.answer("💞 Интересуетесь, как ваши судьбы переплетаются? Узнайте, что числа говорят о вашей "
                              "совместимости с другим человеком!\n\nДля этого введите имя и дату рождения двух "
                              "человек. Например:\n\n\t• Ваше имя и дата рождения: Екатерина, 01.10.2000\n\t• Имя и "
                              "дата рождения вашего партнера: Иван, 22.11.2000\n\n🔍 После расклада вы сможете задать "
                              "вопрос и получить персональный совет для ваших отношений! 💬")
    await state.set_state(Form.waiting_for_data)


