# handlers/user_input_handler.py

import asyncio
import aiosqlite
from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

from calendar_module.calendar_utils import get_user_locale
from calendar_module.schemas import DialogCalendarCallback
from handlers.sections_handler import handle_section
from handlers.start_handler import cmd_start
from keyboards.sections_fate_matrix import create_full_sections_keyboard, create_sections_keyboard, create_reply_keyboard, functions_keyboard
from handlers.numerology_handler import process_selecting_category_num
from services.birthday_service import calculate_values
from services.calendar_service import process_calendar_selection, start_calendar
from services.db_service import get_subscription_details, update_subscription_status, update_user_readings_left
from services.gpt_service import EventHandler, generate_gpt_response_matrix, setup_assistant_and_vector_store
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
async def process_selecting_category(callback_query: CallbackQuery, callback_data: DialogCalendarCallback, state: FSMContext):

    data = await state.get_data()
    category = data.get('category')


    if category == 'matrix':
        await process_selecting_category_matrix(callback_query, callback_data, state)
    elif category == 'numerology':
        await process_selecting_category_num(callback_query, callback_data, state)
    else:

        await callback_query.answer("Неизвестная категория.")


async def process_selecting_category_matrix(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
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
        while response_text is None and attempt < max_retries:
            attempt += 1
            response_text = await generate_gpt_response_matrix(user_name, values, assistant)
            if not response_text:
                print(f"Попытка {attempt}: не удалось сгенерировать ответ.")
        # response_text = "Личные качества:\n\n1. Характер человека: Энергия 12 говорит о человеке, чья внутренняя сила и зона комфорта определяют множество аспектов его жизни. Эта энергия поддерживает связь со всеми другими аспектами жизни, влияя на них положительно или отрицательно в зависимости от своего состояния. Она требует от человека рядом с собой энергии, чтобы поддерживать оптимизм и гармонию. В плюсе она наполняет жизнь светом и радостью, в минусе может тянуть другие жизненные энергии вниз, вызывая негатив и депрессию.\n\n2. Портрет личности: Энергия 31 является отражением внутреннего компаса, который помогает двигаться по жизни. Это позитивное качество, заложенное с рождения, дает человеку ощущение счастья и удовлетворения. Она помогает реализовывать таланты и потенциал, обеспечивая радость бытия. Портрет личности становится путеводителем в общении, работе и отдыхе, наполняя человека сильной и гармоничной энергией.\n\n3. Высшая суть: Внутренний потенциал - энергия 1 предполагает лидерские качества и желание делиться своими идеями, способностями, которые могут остаться неиспользованными из-за страха. Талант от бога - энергия 14 требует поиска связи с душой, творческого самовыражения и избежания крайностей и экстремизма. Навыки прошлого под эгидой энергия 13 говорят о необходимости организации, минимализма и способности завершать начатые дела, что влечет за собой просветление и обновление жизненной энергии.\n\n---\n\nПредназначение:\n\n1. Личное предназначение: энергия 12 указывает на необходимость служения и альтруизма, балансируя между самопожертвованием и заботой о себе. Энергия требует от человека научиться творчески реализовываться, помогая другим и не позволяя использовать свои силы на помощь без взаимной благодарности.\n\n2. Социальное предназначение: энергия 6 усиливает значимость взаимоотношений и коммуникаций с окружающим миром. Она просит видеть во всем красоту и романтику, налаживать связи и создавать гармонию вокруг себя. Это потребность в балансировании между своими желаниями и потребностями окружающих.\n\n3. Духовное предназначение: энергия 18 предлагает работать над страхами и опасениями, искать истину и позитивное мышление, изучать эзотерические науки для решения внутренних проблем. Она ведет к принятию и прощению, позволяя энергетически свободно течь в жизнь.\n\n4. Планетарное предназначение: энергия 6 снова демонстрирует важность коммуникации и любви, как в личном, так и в глобальном масштабе, подчеркивая необходимость взращивать понимание между людьми и вести их к общей гармонии и миру.\n\n---\n\nДетско-родительские отношения:\n\n1. Для чего душа пришла к родителям – энергия 31 отражает желание душой наладить внутренние контакты и связи с окружающим миром. Это оптимизм, стремление к позитиву и обучению через радость. Её задача - обучение жизни через принятие внутренней и внешней стороны жизни, находя гармонию и целостность.\n\n2. Задача отношений – энергия 11 подчеркивает важность силы и потенциала в отношениях. Это энергия, которая указывает на необходимость быть выдержанным и терпеливым, учиться на многослойности жизни и не срываться на конфликты. Она учит осознанию необходимости поддержки и уважения границ.\n\n3. Ошибки во взаимоотношениях с родителями и своими детьми – энергия 7 акцентирует внимание на диагностику недостатков, страхов и ложных представлений, которые перетекли из родительских ошибок. Она указывает на необходимость ухода от сопротивления и борьбы с судьбой, исправления прошлого и движения к духовному озарению.\n\n---\n\nТаланты:\n\n1. Талант от бога – энергия 14 является отображением глубокой связи с душевными аспектами. Эта энергия ведет к раскрытию художественного и духовного потенциала, позволяет гармонично проживать жизнь без крайностей. Она подсказывает, как наполниться творческой энергией и как избегать стрессовых ситуаций.\n\n2. Внутренний потенциал: энергия 1 подчеркивает лидерские качества и способность вдохновлять другим своим примером. Она способствует развивающемуся восприятию и поддерживает новаторские начинания, важность делиться своими открытиями с другим миром.\n\n3. Навык прошлого: энергия 13 говорит о вашем умении аккумулировать произветренческое отношение, когда вы готовы завершать начатые дела и избегать накопительства негативных энергий. Такое отношение способствует освобождению внутренней энергии и обновлению.\n\n---\n\nРодовые программы:\n\n1. Духовные задачи – энергии 5, 11 фокусируются на выше превалирующих задачах, связанных с признанием и развитием внутренней силы. Эта энергия дает импульс для самосозидания через понимание законов Вселенной и построение конструктивной связи с окружающим миром.\n\n2. Материальные задачи – энергии 10, 16 требуют научиться работать с материальными ценностями, привнесение всех возможностей для создания прорывных перемен в своей жизни и преодоления препятствий на пути к благополучию.\n\n---\n\nКармический хвост:\n\nКармический хвост: Энергии 18, 6, 6 показывают на нерешенные задачи прошлого, которые перетягиваются в настоящее существование. Это энергии, которые требуют исправления ошибок и недоработок из прошлых опытов, работа с отношениями и страхами, преодоление внутренней несогласованности.\n\n---\n\nГлавный кармический урок души – энергия 6 подчеркивает важность взаимоотношений и контактов в нашей жизни, выявляет ошибки и недоработки в коммуникации, предлагая исправлять их, развивая понимание и любовь ко всем окружающим.\n\n---\n\nОтношения:\n\n1. Отношения в прошлом: энергия 18 говорит о прежних ошибках в отношениях, которые могут повторяться в настоящем. Это требует избавиться от воспоминаний негативного характера и учиться находить позитивное взаимодействие.\n\n2. Как отношения влияют на финансы: энергия 4 подчеркивает взаимосвязь между личными и деловыми контактами, влияющими на финансовое положение человека, уделяя внимание гармонизации этих аспектов.\n\n3. Кармические отношения: энергия 22 предлагает восприятие того, что кармически задается в текущей жизни. Это направление помогает понять основные аспекты взаимодействий, чтобы лучше осознать сущность происходящих событий.\n\n---\n\nДеньги:\n\n1. Как заработали деньги в прошлом – Энергия 22 предлагает выбрать направление, в котором был достигнут успех, однако важно вывести эту деятельность на положительный уровень и избегать отстаивания старого.\n\n2. Дополнительные возможности – энергия 4 связана с упором на позитивные характеристики, помогающие увеличить финансовый поток, работая с парным сотрудничеством.\n\n3. Сферы высокого финансового потока – энергия 8 открывает наиболее благоприятные области для увеличения доходов, указывая на важность распределения финансов."


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
    print("Обработчик handle_section_callback вызван", callback_query.data)  # Добавьте этот print

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