# handlers/compatibility_handler.py

from aiogram import Router, F, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from calendar_module.calendar_utils import get_user_locale
from calendar_module.schemas import DialogCalendarCallback
from handlers.start_handler import cmd_start
from keyboards.sections_fate_com import create_full_sections_keyboard_com, create_sections_keyboard_com
from keyboards.sections_fate_matrix import functions_keyboard
from handlers.sections_handler import handle_section
from services.birthday_service import calculate_compatibility
from services.calendar_service import process_calendar_selection, start_calendar
from services.db_service import get_subscription_details, update_subscription_status, update_user_readings_left
from services.gpt_service import setup_assistant_and_vector_store
from services.gpt_service_com import generate_gpt_response_com
from services.message_service import delete_messages, notify_subscription_expired, save_message_id
from services.user_service import get_user_data, update_user_date_com, update_user_name
from states import Form
from aiogram.filters.state import StateFilter

router = Router()


@router.callback_query(F.data == "compatibility")
async def handle_numerology(call: CallbackQuery, state: FSMContext):
    await state.update_data(category='compatibility')

    message_text = (
        "✍️ Введите имя партнера №1:"
    )
    await prompt_for_name_compatibility(call, state, message_text, Form.waiting_for_name_first)


async def prompt_for_name_compatibility(call: CallbackQuery, state: FSMContext, message_text: str, next_state: str):

    await call.message.delete()
    prompt_message = await call.message.answer(message_text)
    await state.update_data(prompt_message_id=prompt_message.message_id)
    await save_message_id(state, prompt_message.message_id)
    await state.set_state(next_state)

@router.message(StateFilter(Form.waiting_for_name_first))
async def handle_params_input(message: types.Message, state: FSMContext):
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
        "🗓 Выберите дату рождения партнера №1",
        reply_markup=await start_calendar(locale=await get_user_locale(message.from_user))
    )
    await state.update_data(date_prompt_message_id=date_prompt_message.message_id)
    await save_message_id(state, date_prompt_message.message_id)
    await state.set_state(Form.waiting_for_data_first)


@router.callback_query(DialogCalendarCallback.filter(), StateFilter(Form.waiting_for_data_first))
async def process_selecting_first_partner_date(callback_query: CallbackQuery, callback_data: DialogCalendarCallback, state: FSMContext):
    selected, date = await process_calendar_selection(callback_query, callback_data)

    if selected:
        await update_user_date_com(state, date)

        message_text = "✍️ Введите имя партнера №2:"
        await prompt_for_name_compatibility(callback_query, state, message_text, Form.waiting_for_name_second)


@router.message(StateFilter(Form.waiting_for_name_second))
async def handle_second_partner_name(message: types.Message, state: FSMContext):
    partner_name = message.text
    await state.update_data(partner_name=partner_name)

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
        print(f"Ошибка при удалении сообщения с именем партнера: {e}")

    date_prompt_message = await message.answer(
        "🗓 Выберите дату рождения партнера №2",
        reply_markup=await start_calendar(locale=await get_user_locale(message.from_user))
    )
    await state.update_data(date_prompt_message_id=date_prompt_message.message_id)
    await save_message_id(state, date_prompt_message.message_id)
    await state.set_state(Form.waiting_for_data_second)


@router.callback_query(DialogCalendarCallback.filter(), StateFilter(Form.waiting_for_data_second))
async def process_selecting_second_partner_date(callback_query: CallbackQuery, callback_data: DialogCalendarCallback, state: FSMContext):
    selected, date = await process_calendar_selection(callback_query, callback_data)

    
    if selected:
        await update_user_date_com(state, date, partner="second")

        data = await state.get_data()
        user_name, _ = await get_user_data(state)

        first_partner_date = data.get("date_first_partner")
        second_partner_date = data.get("date_second_partner")

        if not first_partner_date or not second_partner_date:
            await callback_query.message.answer("Ошибка: не удалось получить даты партнеров.")
            return

        previous_message_id = data.get("date_prompt_message_id")

        if previous_message_id:
            try:
                await callback_query.message.bot.delete_message(chat_id=callback_query.message.chat.id, message_id=previous_message_id)
            except Exception as e:
                print(f"Ошибка при удалении сообщения с календарем: {e}")

        generating_message = await callback_query.message.answer("Подождите минутку, мы готовим для вас ответ ⏳")
        assistant = await setup_assistant_and_vector_store()
        first_partner_day = first_partner_date.day
        first_partner_month = first_partner_date.month
        first_partner_year = first_partner_date.year

        second_partner_day = second_partner_date.day
        second_partner_month = second_partner_date.month
        second_partner_year = second_partner_date.year

        values = calculate_compatibility(
            (first_partner_day, first_partner_month, first_partner_year),
            (second_partner_day, second_partner_month, second_partner_year)
        ) 
        response_text = None
        max_retries = 10
        attempt = 0
        while response_text is None and attempt < max_retries:
            attempt += 1
            response_text = await generate_gpt_response_com(user_name, values, assistant)
            if not response_text:
                print(f"Попытка {attempt}: не удалось сгенерировать ответ.")

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
            "Для чего пара встретилась",
            "Как пара выглядит для других",
            "Общая атмосфера внутри пары",
            "Что укрепляет союз",
            "Финансы",
            "Желания и цели",
            "Задачи пары",
            "Трудности и недопонимания",
        ]

        categories_dict = {category: split_text[i].strip() for i, category in enumerate(categories) if i < len(split_text)}

        await state.update_data(full_response=categories_dict)
        user_id = callback_query.from_user.id
        subscription_details = await get_subscription_details(user_id)
        subscription_active = subscription_details["subscription_active"]
        readings_left = subscription_details["readings_left"]
        questions_left = subscription_details["questions_left"]
        
        if subscription_active:  
            sections_keyboard = create_full_sections_keyboard_com()
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
        else:
            sections_keyboard = create_sections_keyboard_com()
            first_message = await callback_query.message.answer(
                "Ура, ваш расчет по совместимости готов 💕\n\n"
                "Вы можете посмотреть расклад по каждому из разделов.\n"
                "✅ - доступно бесплатно\n"
                "🔐 - требуется полный доступ",
                reply_markup=sections_keyboard
            )
            await state.update_data(first_message_id=first_message.message_id)
            await save_message_id(state, first_message.message_id)

            three_functions = functions_keyboard()
            question_prompt_message = await callback_query.message.answer(
                f"Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
                " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
                "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)",
                reply_markup=three_functions,
                parse_mode="HTML"
            )
            await state.update_data(question_prompt_message_id=question_prompt_message.message_id)
            await save_message_id(state, question_prompt_message.message_id)

@router.callback_query(lambda callback: callback.data.startswith("com_"))
async def handle_section_callback_num(callback_query: CallbackQuery, state: FSMContext):
    category_mapping = {
        "com_meeting_purpose": "Для чего пара встретилась",
        "com_appearance": "Как пара выглядит для других",
        "com_atmosphere": "Общая атмосфера внутри пары",
        "com_strengthen_union": "Что укрепляет союз",
        "com_finances": "Финансы",
        "com_wishes_goals": "Желания и цели",
        "com_tasks": "Задачи пары",
        "com_difficulties": "Трудности и недопонимания",
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
        "Для чего пара встретилась",
        "Как пара выглядит для других"
    ]:
        warning_message = await callback_query.message.answer(
            "Эта категория доступна только в платной версии. Пожалуйста, откройте полный доступ."
        )
        await state.update_data(previous_warning_message_id=warning_message.message_id)
        await save_message_id(state, warning_message.message_id)
        return

    if subscription_active and readings_left <= 0 and category not in [
        "Для чего пара встретилась",
        "Как пара выглядит для других"
    ]:
        await notify_subscription_expired(callback_query, state)
        return

    if subscription_active and category not in [
        "Для чего пара встретилась",
        "Как пара выглядит для других"
    ]:
        new_readings_left = readings_left - 1
        await update_user_readings_left(user_id, new_readings_left)
    
    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])
    await handle_section(callback_query, state, category)

