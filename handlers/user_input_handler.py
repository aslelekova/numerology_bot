# handlers/user_input_handler.py

import asyncio
import aiosqlite
from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

from calendar_module.calendar_utils import get_user_locale
from calendar_module.schemas import DialogCalAct, DialogCalendarCallback
from handlers.sections_handler import handle_section
from handlers.start_handler import cmd_start
from keyboards.sections_fate_matrix import create_full_sections_keyboard, create_sections_keyboard, create_reply_keyboard, functions_keyboard
from services.birthday_service import calculate_values
from services.calendar_service import process_calendar_selection, start_calendar
from services.db_service import get_subscription_details, update_subscription_status, update_user_readings_left
from services.gpt_service import EventHandler, setup_assistant_and_vector_store
from services.message_service import delete_messages, notify_subscription_expired
from services.user_service import update_user_name, get_user_data, update_user_date
from states import Form

router = Router()


async def prompt_for_name(call: CallbackQuery, state: FSMContext, message_text: str, next_state: str):
    """
    Prompts the user to enter their name by sending a message and updating the state.

    :param call: The callback query object containing information about the callback event.
    :param state: The FSM (Finite State Machine) context to manage the state of the conversation.
    :param message_text: The text message to prompt the user for their name.
    :param next_state: The next state in the FSM after the user responds.
    :return: None
    """
    await call.message.delete()
    prompt_message = await call.message.answer(message_text)
    await state.update_data(prompt_message_id=prompt_message.message_id)
    await state.set_state(next_state)


@router.message(StateFilter(Form.waiting_for_name))
async def handle_params_input(message: types.Message, state: FSMContext):
    """
    Handles user input for their name, updates the state, and prompts the user to select a date of birth.

    :param message: The message object containing the user's input.
    :param state: The FSM (Finite State Machine) context to manage the state of the conversation.
    :return: None
    """
    user_name = message.text
    await update_user_name(state, user_name)

    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")

    if prompt_message_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    try:
        await message.delete()

    except Exception as e:
        print(f"Ошибка при удалении сообщения с именем пользователя: {e}")

    date_prompt_message = await message.answer(
        "Выберите дату рождения 👇",
        reply_markup=await start_calendar(locale=await get_user_locale(message.from_user))
    )
    await state.update_data(date_prompt_message_id=date_prompt_message.message_id)
    await state.set_state(Form.waiting_for_data)


@router.callback_query(DialogCalendarCallback.filter())
async def process_selecting_category(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await process_calendar_selection(callback_query, callback_data)

    if selected:
        user_name, _ = await get_user_data(state)
        await update_user_date(state, date)

        day, month, year = date.day, date.month, date.year
        values = calculate_values(day, month, year)
        data = await state.get_data()
        previous_message_id = data.get("date_prompt_message_id")

        if previous_message_id:
            try:
                await callback_query.message.bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)
            except Exception as e:
                print(f"Ошибка при удалении сообщения с календарем: {e}")

        generating_message = await callback_query.message.answer("⏳")
        assistant = await setup_assistant_and_vector_store()

        response_text = None
        max_retries = 10
        attempt = 0
        # while response_text is None and attempt < max_retries:
        #     attempt += 1
        #     response_text = await generate_gpt_response_matrix(user_name, values, assistant)
        #     if not response_text:
        #         print(f"Попытка {attempt}: не удалось сгенерировать ответ.")


        await state.update_data(response_text=response_text)

        await generating_message.delete()

        if not response_text:
            await callback_query.message.answer(
                "Не удалось сгенерировать ответ. Пожалуйста, повторите попытку.",
            )
            await cmd_start(callback_query.message, state)
            return

        response_text = response_text.replace("#", "").replace("*", "")
        split_text = response_text.split("---")
        categories = [
            "Личные качества",
            "Предназначение",
            "Детско-родительские отношения",
            "Таланты",
            "Родовые программы",
            "Кармический хвост",
            "Главный кармический урок",
            "Отношения",
            "Деньги"
        ]

        categories_dict = {category: split_text[i].strip() for i, category in enumerate(categories) if i < len(split_text)}

        await state.update_data(full_response=categories_dict)
        user_id = callback_query.from_user.id
        subscription_details = await get_subscription_details(user_id)
        subscription_active = subscription_details["subscription_active"]
        readings_left = subscription_details["readings_left"]
        questions_left = subscription_details["questions_left"]
        
        if subscription_active:  
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
        else:
            sections_keyboard = create_sections_keyboard()
            first_message = await callback_query.message.answer(
                "Ура, ваша матрица судьбы готова 🔮\n\n"
                "Вы можете посмотреть расклад по каждому из разделов.\n"
                "✅ - доступно бесплатно\n"
                "🔐 - требуется полный доступ",
                reply_markup=sections_keyboard
            )
            await state.update_data(first_message_id=first_message.message_id)

            three_functions = functions_keyboard()
            question_prompt_message = await callback_query.message.answer(
                f"Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
                " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
                "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)",
                reply_markup=three_functions,
                parse_mode="HTML"
            )
            await state.update_data(question_prompt_message_id=question_prompt_message.message_id)


@router.callback_query(lambda callback: callback.data.startswith("section_"))
async def handle_section_callback(callback_query: CallbackQuery, state: FSMContext):
    category_mapping = {
        "section_personal": "Личные качества",
        "section_destiny": "Предназначение",
        "section_talents": "Таланты",
        "section_family_relationships": "Детско-родительские отношения",
        "section_generic_programs": "Родовые программы",
        "section_karmic_tail": "Кармический хвост",
        "section_karmic_lesson": "Главный кармический урок",
        "section_relationships": "Отношения",
        "section_money": "Деньги",
    }

    category = category_mapping.get(callback_query.data, "Неизвестная категория")

    data = await state.get_data()
    first_message_id = data.get("first_message_id")
    question_prompt_message_id = data.get("question_prompt_message_id")
    previous_warning_message_id = data.get("previous_warning_message_id")

    if previous_warning_message_id:
        try:
            await callback_query.message.bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_warning_message_id)
        except Exception as e:
            print(f"Ошибка при удалении предыдущего предупреждающего сообщения: {e}")

    user_id = callback_query.from_user.id
    subscription_details = await get_subscription_details(user_id)
    subscription_active = subscription_details["subscription_active"]
    readings_left = subscription_details["readings_left"]
    questions_left = subscription_details["questions_left"]

    if readings_left <= 0 and questions_left <= 0:
        await update_subscription_status(user_id, 0)

    if not subscription_active and category not in [
        "Личные качества",
        "Предназначение",
        "Таланты",
        "Детско-родительские отношения"
    ]:
        warning_message = await callback_query.message.answer(
            "Эта категория доступна только в платной версии. Пожалуйста, откройте полный доступ."
        )
        await state.update_data(previous_warning_message_id=warning_message.message_id)
        return

    if subscription_active and readings_left <= 0 and category not in [
        "Личные качества",
        "Предназначение",
        "Таланты",
        "Детско-родительские отношения"
    ]:
        await notify_subscription_expired(callback_query, state)
        return

    if subscription_active and category not in [
        "Личные качества",
        "Предназначение",
        "Таланты",
        "Детско-родительские отношения"
    ]:
        new_readings_left = readings_left - 1
        await update_user_readings_left(user_id, new_readings_left)
    
    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])
    await handle_section(callback_query, state, category)


@router.callback_query(lambda callback: callback.data == "my_tariff")
async def show_current_tariff(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    user_id = callback_query.from_user.id

    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT tariff, readings_left, questions_left, subscription_active FROM login_id WHERE id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()

    if result:
        tariff_number, readings_left, questions_left, subscription_active = result
        if tariff_number == "Тариф 1":
            tariff_price = "290 рублей"
        elif tariff_number == "Тариф 2":
            tariff_price = "450 рублей"
        elif tariff_number == "Тариф 3":
            tariff_price = "650 рублей"
        else:
            tariff_price = "Нет активного тарифа"

        status_message = (
            f"Ваш тариф: {tariff_price}\n\n"
            f"💫 У вас осталось:\n"
            f"• 🔮 {readings_left} любых раскладов\n"
            f"• ⚡️ {questions_left} ответа на любые вопросы\n\n"
            "Обновить тариф?"
        )

        new_message = await callback_query.message.answer(
            status_message,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Обновить тариф", callback_data="get_full_access_main")],
                [InlineKeyboardButton(text="Назад", callback_data="main_menu")]
            ])
        )

        await state.update_data(tariff_message_id=new_message.message_id)
    else:
        await callback_query.message.answer("Ошибка: информация о тарифе не найдена.")
