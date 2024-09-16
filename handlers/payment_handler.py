import requests
from yookassa import Configuration, Payment
import uuid
import traceback
from aiogram.fsm.context import FSMContext
from aiogram import Router, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from services.message_service import delete_messages, send_initial_messages
from keyboards.sections_fate_matrix import create_sections_keyboard, functions_keyboard
from config import secret_key, shop_id
  
router = Router()

Configuration.account_id = shop_id
Configuration.secret_key = secret_key

@router.callback_query(lambda callback: callback.data == "get_full_access")
async def handle_full_access(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    first_message_id = data.get("first_message_id")
    question_prompt_message_id = data.get("question_prompt_message_id")

    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])

    payment_url_1, _ = await create_payment("290.00", callback_query.message.chat.id, "Тариф 1. 290 руб")
    payment_url_2, _ = await create_payment("450.00", callback_query.message.chat.id, "Тариф 2. 450 руб")
    payment_url_3, _ = await create_payment("650.00", callback_query.message.chat.id, "Тариф 3. 650 руб")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="290 руб", url=payment_url_1)],
            [InlineKeyboardButton(text="450 руб", url=payment_url_2),
             InlineKeyboardButton(text="650 руб", url=payment_url_3)],
            [InlineKeyboardButton(text="Назад", callback_data="back")]
        ]
    )

    await callback_query.message.answer(
        "Мы подготовили для тебя 3 тарифа 💫\n\nТариф 1.  290 рублей\n🔮 5 любых раскладов\n⚡️ 10 ответов на любые вопросы \n\nТариф 2.  450 рублей  (популярный)\n🔮 8 любых раскладов\n⚡️ 20 ответов на любые вопросы \n\nТариф 3.  650 рублей \n🔮 15 любых раскладов\n⚡️ 40 ответов на любые вопросы \n\nВыберите один из тарифов",
        reply_markup=keyboard
    )



async def create_payment(amount, chat_id, description):
    try:
        payment = Payment.create({
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/MakeMyMatrix_Bot"
            },
            "capture": True,
            "description": description,
            "receipt": {
                "customer": {
                    "full_name": "Имя Фамилия",
                    "email": "example@example.com",
                    "phone": "+79000000000"
                },
                "items": [
                    {
                        "description": "Услуга по созданию матрицы судьбы",
                        "quantity": "1.00",
                        "amount": {
                            "value": amount,
                            "currency": "RUB"
                        },
                        "vat_code": 1,
                        "payment_mode": "full_prepayment",
                        "payment_subject": "service"
                    }
                ]
            }
        }, uuid.uuid4())

        return payment.confirmation.confirmation_url, payment.id
    except Exception as e:
        print(f"Ошибка при создании платежа: {e}")
        print(f"Параметры платежа: Amount: {amount}, Currency: RUB")
        print(traceback.format_exc())

