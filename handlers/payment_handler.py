import aiosqlite
from yookassa import Configuration, Payment
import uuid
import traceback
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from handlers.start_handler import cmd_start
from keyboards.sections_fate_com import create_full_sections_keyboard_com, create_sections_keyboard_com
from keyboards.sections_numerology import create_full_sections_keyboard_num, create_sections_keyboard_num
from services.db_service import get_subscription_details
from services.message_service import delete_message, delete_messages, send_initial_messages, save_message_id
from keyboards.sections_fate_matrix import create_full_sections_keyboard, create_sections_keyboard, create_tariff_keyboard, functions_keyboard
from config import secret_key, shop_id
  
router = Router()

Configuration.account_id = shop_id
Configuration.secret_key = secret_key


@router.callback_query(lambda callback: callback.data == "get_full_access")
async def handle_full_access(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    first_message_id = data.get("first_message_id")
    question_prompt_message_id = data.get("question_prompt_message_id")
    previous_warning_message_id = data.get("previous_warning_message_id")
    if previous_warning_message_id:
        try:
            await callback_query.message.bot.delete_message(chat_id=callback_query.message.chat.id,
                                                            message_id=previous_warning_message_id)
        except Exception as e:
            print(f"Ошибка при удалении предыдущего предупреждающего сообщения: {e}")

    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])

    payment_url_1, payment_id_1 = await create_payment("290.00", callback_query.message.chat.id, "Тариф 1. 290 руб")
    payment_url_2, payment_id_2 = await create_payment("450.00", callback_query.message.chat.id, "Тариф 2. 450 руб")
    payment_url_3, payment_id_3 = await create_payment("650.00", callback_query.message.chat.id, "Тариф 3. 650 руб")

    await state.update_data(payment_id_1=payment_id_1, payment_id_2=payment_id_2, payment_id_3=payment_id_3)

    keyboard = create_tariff_keyboard(payment_url_1, payment_url_2, payment_url_3)

    tariff_message1 = await callback_query.message.answer(
        "Мы подготовили для тебя 3 тарифа 💫\n\nТариф 1.  290 рублей\n🔮 5 любых раскладов\n⚡️ 10 ответов на любые вопросы \n\n"
        "Тариф 2.  450 рублей  (популярный)\n🔮 8 любых раскладов\n⚡️ 20 ответов на любые вопросы \n\n"
        "Тариф 3.  650 рублей \n🔮 15 любых раскладов\n⚡️ 40 ответов на любые вопросы \n\n"
        "Выберите один из тарифов",
        reply_markup=keyboard
    )
    await save_message_id(state, tariff_message1.message_id)

    await state.update_data(tariff_message_id=tariff_message1.message_id)

    confirmation_message1 = await callback_query.message.answer(
        "После оплаты нажмите кнопку ниже, чтобы проверить статус платежа:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Проверить оплату", callback_data=f"check_payment")]
            ]
        )
    )
    await save_message_id(state, confirmation_message1.message_id)
    await state.update_data(confirmation_message_id=confirmation_message1.message_id)



@router.callback_query(lambda callback: callback.data == "get_full_access_main")
async def handle_full_access_main(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    tariff_message_id = data.get("tariff_message_id")
    
    await delete_message(callback_query.bot, callback_query.message.chat.id, tariff_message_id)

    payment_url_1, payment_id_1 = await create_payment("1.00", callback_query.message.chat.id, "Тариф 1. 290 руб")
    payment_url_2, payment_id_2 = await create_payment("2.00", callback_query.message.chat.id, "Тариф 2. 450 руб")
    payment_url_3, payment_id_3 = await create_payment("3.00", callback_query.message.chat.id, "Тариф 3. 650 руб")

    await state.update_data(payment_id_1=payment_id_1, payment_id_2=payment_id_2, payment_id_3=payment_id_3)

    keyboard = create_tariff_keyboard(payment_url_1, payment_url_2, payment_url_3, "main_menu")

    tariff_message = await callback_query.message.answer(
        "Мы подготовили для тебя 3 тарифа 💫\n\nТариф 1.  290 рублей\n🔮 5 любых раскладов\n⚡️ 10 ответов на любые вопросы \n\n"
        "Тариф 2.  450 рублей  (популярный)\n🔮 8 любых раскладов\n⚡️ 20 ответов на любые вопросы \n\n"
        "Тариф 3.  650 рублей \n🔮 15 любых раскладов\n⚡️ 40 ответов на любые вопросы \n\n"
        "Выберите один из тарифов",
        reply_markup=keyboard
    )
    await save_message_id(state, tariff_message.message_id)

    await state.update_data(tariff_message_id=tariff_message.message_id)

    confirmation_message = await callback_query.message.answer(
        "После оплаты нажмите кнопку ниже, чтобы проверить статус платежа:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Проверить оплату", callback_data=f"check_payment")]
            ]
        )
    )
    await save_message_id(state, confirmation_message.message_id)

    await state.update_data(confirmation_message_id=confirmation_message.message_id)


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

    payment_id_1 = data.get("payment_id_1")
    payment_id_2 = data.get("payment_id_2")
    payment_id_3 = data.get("payment_id_3")

    if not any([payment_id_1, payment_id_2, payment_id_3]):
        await callback_query.message.answer("Ошибка: идентификаторы платежей не найдены.")
        return

    payment_ids = [payment_id_1, payment_id_2, payment_id_3]

    try:
        pending = False

        for payment_id in payment_ids:
            if payment_id:
                payment = Payment.find_one(payment_id)

                if payment.status == "succeeded":
                    await update_user_tariff(callback_query, callback_query.message.chat.id, payment.description)
                    success = await callback_query.message.answer("Оплата прошла успешно! 🎉 Полный доступ предоставлен.")
                    data = await state.get_data()
                    await save_message_id(state, success.message_id)

                    confirmation_message_id1 = data.get("confirmation_message_id1")
                    tariff_message1 = data.get("tariff_message1")

                    if tariff_message1:
                            try:
                                await callback_query.message.bot.delete_message(
                                    chat_id=callback_query.message.chat.id,
                                    message_id=tariff_message1
                                )
                            except Exception as e:
                                if "message to delete not found" not in str(e):
                                    print(f"Error deleting tarif message with ID {tariff_message1}: {e}")


                    if confirmation_message_id1:
                        try:
                            await callback_query.message.bot.delete_message(
                                chat_id=callback_query.message.chat.id,
                                message_id=confirmation_message_id1
                            )
                        except Exception as e:
                            if "message to delete not found" not in str(e):
                                print(f"Error deleting confirmation message with ID {confirmation_message_id1}: {e}")

                    tariff_message = data.get("tariff_message_id")
                    confirmation_message_id = data.get("confirmation_message_id")
                    if tariff_message:
                        try:
                            await callback_query.message.bot.delete_message(
                                chat_id=callback_query.message.chat.id,
                                message_id=tariff_message
                            )
                        except Exception as e:
                            if "message to delete not found" not in str(e):
                                print(f"Error deleting tarif message with ID {tariff_message}: {e}")


                    if confirmation_message_id:
                        try:
                            await callback_query.message.bot.delete_message(
                                chat_id=callback_query.message.chat.id,
                                message_id=confirmation_message_id
                            )
                        except Exception as e:
                            if "message to delete not found" not in str(e):
                                print(f"Error deleting confirmation message with ID {confirmation_message_id}: {e}")

                    user_id = callback_query.from_user.id
                    subscription_details = await get_subscription_details(user_id)
                    readings_left = subscription_details["readings_left"]
                    questions_left = subscription_details["questions_left"]

                    category = data.get('category')
                    if category == 'matrix':
                        sections_keyboard=create_full_sections_keyboard()
                    elif category == 'numerology':
                        sections_keyboard=create_full_sections_keyboard_num()
                    elif category == 'compatibility':
                        sections_keyboard=create_full_sections_keyboard_com()
                    elif category is None:
                        await cmd_start(callback_query.message, state)
                        return

                    first_message = await callback_query.message.answer(
                        f"У вас осталось:\n🔮 {readings_left} любых раскладов\n⚡️ {questions_left} ответа на любые вопросы",
                        reply_markup=sections_keyboard
                    )
                    await state.update_data(first_message_id=first_message.message_id)
                    await save_message_id(state, first_message.message_id)

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
                    await save_message_id(state, question_prompt_message.message_id)

                    await state.update_data(question_prompt_message_id=question_prompt_message.message_id)
                    return

                elif payment.status == "pending":
                    pending = True
                else:
                    continue

        if pending:
            pending_message = await callback_query.message.answer("Оплата пока не завершена. Пожалуйста, попробуйте позже.")
            await save_message_id(state, pending_message.message_id)

        else:
            failed_message = await callback_query.message.answer("Оплата не прошла. Попробуйте снова.")
            await save_message_id(state, failed_message.message_id)

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
        async with aiosqlite.connect('/app/users.db') as connect:
            await connect.execute("""
                UPDATE login_id
                SET tariff = ?, readings_left = ?, questions_left = ?, subscription_active = 1
                WHERE id = ?
            """, (tariff, readings_left, questions_left, chat_id))
            await connect.commit()


@router.callback_query(lambda callback: callback.data == "back")
async def handle_back_button(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    confirmation_message_id1 = data.get("confirmation_message_id1")
    tariff_message1 = data.get("tariff_message1")
    confirmation_message_id = data.get("confirmation_message_id")
    tariff_message_id = data.get("tariff_message_id")

    if tariff_message_id:
            try:
                await callback_query.message.bot.delete_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=tariff_message_id
                )
            except Exception as e:
                if "message to delete not found" not in str(e):
                    print(f"Error deleting tarif message with ID {tariff_message_id}: {e}")

    if confirmation_message_id:
        try:
            await callback_query.message.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=confirmation_message_id
            )
        except Exception as e:
            if "message to delete not found" not in str(e):
                print(f"Error deleting confirmation message with ID {confirmation_message_id}: {e}")


    if tariff_message1:
            try:
                await callback_query.message.bot.delete_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=tariff_message1
                )
            except Exception as e:
                if "message to delete not found" not in str(e):
                    print(f"Error deleting tarif message with ID {tariff_message1}: {e}")
                    

    if confirmation_message_id1:
        try:
            await callback_query.message.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=confirmation_message_id1
            )
        except Exception as e:
            if "message to delete not found" not in str(e):
                print(f"Error deleting confirmation message with ID {confirmation_message_id1}: {e}")



    user_id = callback_query.from_user.id
    subscription_details = await get_subscription_details(user_id)
    subscription_active = subscription_details["subscription_active"]
    readings_left = subscription_details["readings_left"]
    questions_left = subscription_details["questions_left"]
    category = data.get('category')
    if category == 'matrix':
        reply_markup=create_full_sections_keyboard()
    elif category == 'numerology':
        reply_markup=create_full_sections_keyboard_num()
    elif category == 'compatibility':
        reply_markup=create_full_sections_keyboard_com()
    else:
        await callback_query.answer("Неизвестная категория.")

    if subscription_active:
        first_message = await callback_query.message.answer(
            f"У вас осталось:\n🔮 {readings_left} любых раскладов\n⚡️ {questions_left} ответа на любые вопросы",
            reply_markup=reply_markup
        )
        await state.update_data(first_message_id=first_message.message_id)
        await save_message_id(state, first_message.message_id)

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
        await save_message_id(state, question_prompt_message.message_id)

    else:
        if category == 'matrix':
            section_message = "Ура, ваша матрица судьбы готова 🔮\n\nВы можете посмотреть расклад по каждому из разделов.\n✅ - доступно бесплатно\n🔐 - требуется полный доступ"
        elif category == 'numerology':
            section_message = "Ура, ваш расчет по Нумерологии | Личному успеху | Финансам готов 💸\n\nВы можете посмотреть расклад по каждому из разделов.\n✅ - доступно бесплатно\n🔐 - требуется полный доступ"
        elif category == 'compatibility':
            section_message = "Ура, ваш расчет по Совместимости готов 💕\n\nВы можете посмотреть расклад по каждому из разделов.\n✅ - доступно бесплатно\n🔐 - требуется полный доступ"
        question_message = ("Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
                            " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
                            "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)")

        if category == 'matrix':
            await send_initial_messages(callback_query.bot, callback_query.message.chat.id, state, section_message, question_message, create_sections_keyboard(), functions_keyboard())
        elif category == 'numerology':
            await send_initial_messages(callback_query.bot, callback_query.message.chat.id, state, section_message, question_message, create_sections_keyboard_num(), functions_keyboard())
        elif category == 'compatibility':
            await send_initial_messages(callback_query.bot, callback_query.message.chat.id, state, section_message, question_message, create_sections_keyboard_com(), functions_keyboard())
        else:
            await callback_query.answer("Неизвестная категория.")

