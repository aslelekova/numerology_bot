from yookassa import Configuration, Payment
import uuid
import traceback
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from services.message_service import delete_messages, send_initial_messages
from keyboards.sections_fate_matrix import create_sections_keyboard, functions_keyboard
from config import secret_key, shop_id

router = Router()

Configuration.account_id = shop_id
Configuration.secret_key = secret_key

print(shop_id, secret_key)
@router.callback_query(lambda callback: callback.data == "get_full_access")
async def handle_full_access(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    first_message_id = data.get("first_message_id")
    question_prompt_message_id = data.get("question_prompt_message_id")

    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="290 руб", callback_data="tariff_1")],
            [InlineKeyboardButton(text="450 руб", callback_data="tariff_2"),
             InlineKeyboardButton(text="650 руб", callback_data="tariff_3")],
             [InlineKeyboardButton(text="Назад", callback_data="back")]
        ]
    )

    await callback_query.message.answer(
        "Мы подготовили для тебя 3 тарифа 💫\n\nТариф 1.  290 рублей\n🔮 5 любых раскладов\n⚡️ 10 ответов на любые вопросы \n\nТариф 2.  450 рублей  (популярный)\n🔮 8 любых раскладов\n⚡️ 20 ответов на любые вопросы \n\nТариф 3.  650 рублей \n🔮 15 любых раскладов\n⚡️ 40 ответов на любые вопросы \n\nВыберите один из тарифов",
        reply_markup=keyboard
    )


async def create_payment(amount, description):


    try:
        payment = Payment.create({
            "amount": {
                "value": f"{amount}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/MakeMyMatrix_Bot"
            },
            "capture": True,
            "description": description
        }, uuid.uuid4())

        return payment.confirmation.confirmation_url
    except Exception as e:
        print(f"Ошибка при создании платежа: {e}")
        print(f"Параметры платежа: Amount: {amount}, Currency: RUB, Description: {description}")
        print(traceback.format_exc())



@router.callback_query(lambda callback: callback.data == "tariff_1")
async def handle_tariff_1(callback_query: CallbackQuery):
    confirmation_url = await create_payment("290.00", "Тариф 1: 290 рублей")
    
    if confirmation_url:
        await callback_query.message.answer(f"Для завершения оплаты перейдите по ссылке: {confirmation_url}")
    else:
        await callback_query.message.answer("Произошла ошибка при создании платежа. Попробуйте позже.")


@router.callback_query(lambda callback: callback.data == "tariff_2")
async def handle_tariff_2(callback_query: CallbackQuery):

    confirmation_url = await create_payment(450, "Тариф 2: 450 рублей")
    
    if confirmation_url:
        await callback_query.message.answer(f"Для завершения оплаты перейдите по ссылке: {confirmation_url}")
    else:
        await callback_query.message.answer("Произошла ошибка при создании платежа. Попробуйте позже.")


@router.callback_query(lambda callback: callback.data == "tariff_3")
async def handle_tariff_3(callback_query: CallbackQuery):

    confirmation_url = await create_payment(650, "Тариф 3: 650 рублей")
    
    if confirmation_url:
        await callback_query.message.answer(f"Для завершения оплаты перейдите по ссылке: {confirmation_url}")
    else:
        await callback_query.message.answer("Произошла ошибка при создании платежа. Попробуйте позже.")


async def check_payment_status(payment_id):
    payment_info = Payment.find_one(payment_id)
    return payment_info.status


@router.callback_query(lambda callback: callback.data == "back")
async def handle_back_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    section_message = "Ура, ваша матрица судьбы готова 🔮\n\nВы можете посмотреть расклад по каждому из разделов.\n✅ - доступно бесплатно\n🔐 - требуется полный доступ"
    question_message = ("Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
                        " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
                        "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)")
    await send_initial_messages(callback_query.bot, callback_query.message.chat.id, state, section_message, question_message, create_sections_keyboard(), functions_keyboard())
