import sqlite3
import requests
from yookassa import Configuration, Payment
import uuid
import traceback
from aiogram.fsm.context import FSMContext
from aiogram import Router, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from services.db_service import get_subscription_details
from services.message_service import delete_messages, send_initial_messages
from keyboards.sections_fate_matrix import create_full_sections_keyboard, create_sections_keyboard, functions_keyboard
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

    payment_url_1, payment_id_1 = await create_payment("1.00", callback_query.message.chat.id, "Тариф 1. 290 руб")
    payment_url_2, payment_id_2 = await create_payment("1.00", callback_query.message.chat.id, "Тариф 2. 450 руб")
    payment_url_3, payment_id_3 = await create_payment("1.00", callback_query.message.chat.id, "Тариф 3. 650 руб")

    await state.update_data(payment_id=payment_id_1)

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

    await callback_query.message.answer(
        "После оплаты нажмите кнопку ниже, чтобы проверить статус платежа:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Проверить оплату", callback_data=f"check_payment")],
                [InlineKeyboardButton(text="Назад", callback_data="back")]
            ]
        )
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
        print(traceback.format_exc())

@router.callback_query(lambda callback: callback.data == "check_payment")
async def check_payment_status(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment_id = data.get("payment_id")  

    if not payment_id:
        await callback_query.message.answer("Ошибка: идентификатор платежа не найден.")
        return

    try:
        payment = Payment.find_one(payment_id)

        if payment.status == "succeeded":
            await update_user_tariff(callback_query, callback_query.message.chat.id, payment.description)
            await callback_query.message.answer("Оплата прошла успешно! 🎉 Полный доступ предоставлен.")
            user_id = callback_query.from_user.id

            subscription_details = await get_subscription_details(user_id)
            readings_left = subscription_details["readings_left"]
            questions_left = subscription_details["questions_left"]
            sections_keyboard = create_full_sections_keyboard()
            first_message = await callback_query.message.answer(
                f"У вас осталось:\n🔮 {readings_left} любых раскладов\n⚡️ {questions_left} ответа на любые вопросы",
                reply_markup=sections_keyboard
            )
            await state.update_data(first_message_id=first_message.message_id)

            question_prompt_message = await callback_query.message.answer(
                    f"Сделайте новый расчет:  \n🔮 Матрица судьбы\n💸 Нумерология | Личному успеху | Финансам\n💕 Совместимость с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
                "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Новый расчет", callback_data="main_menu")],
                    [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_free_question")],
                    [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
                    ]),
                    parse_mode="HTML"
                )

            await state.update_data(question_prompt_message_id=question_prompt_message.message_id)
        elif payment.status == "pending":
            await callback_query.message.answer("Оплата пока не завершена. Пожалуйста, попробуйте позже.")
        else:
            await callback_query.message.answer("Оплата не прошла. Попробуйте снова.")
    except Exception as e:
        print(f"Ошибка при проверке платежа: {e}")
        print(traceback.format_exc())
        await callback_query.message.answer("Произошла ошибка при проверке платежа. Пожалуйста, свяжитесь с поддержкой.")


async def update_user_tariff(callback_query: CallbackQuery, chat_id, description):
    user_id = callback_query.from_user.id

    subscription_details = await get_subscription_details(user_id)
    readings_left = subscription_details["readings_left"]
    questions_left = subscription_details["questions_left"]
    tariff = None

    if "Тариф 1" in description:
        tariff = "Тариф 1"
        readings_left += 5
        questions_left += 10
    elif "Тариф 2" in description:
        tariff = "Тариф 2"
        readings_left += 8
        questions_left += 20
    elif "Тариф 3" in description:
        tariff = "Тариф 3"
        readings_left += 15
        questions_left += 40

    if tariff:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()

        cursor.execute("""
            UPDATE login_id
            SET tariff = ?, readings_left = ?, questions_left = ?, subscription_active = 1
            WHERE id = ?
        """, (tariff, readings_left, questions_left, chat_id))

        connect.commit()
        connect.close()



@router.callback_query(lambda callback: callback.data == "back")
async def handle_back_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    section_message = "Ура, ваша матрица судьбы готова 🔮\n\nВы можете посмотреть расклад по каждому из разделов.\n✅ - доступно бесплатно\n🔐 - требуется полный доступ"
    question_message = ("Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
                        " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
                        "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)")
    await send_initial_messages(callback_query.bot, callback_query.message.chat.id, state, section_message, question_message, create_sections_keyboard(), functions_keyboard())
