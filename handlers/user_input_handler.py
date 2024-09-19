# handlers/user_input_handler.py

import sqlite3
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
from services.birthday_service import calculate_values
from services.calendar_service import process_calendar_selection, start_calendar
from services.db_service import get_subscription_details, update_subscription_status, update_user_readings_left
from services.gpt_service import EventHandler, generate_gpt_response
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

        response_text = None
        max_retries = 10
        attempt = 0
        response_text = "Личные качества:\n\n1. Характер человека: Энергия 10\nЭнергия 10 предполагает, что личность окружена удачей и везением. Этот человек может с легкостью привлекать положительные события в свою жизнь. В положительном аспекте он доверяет высшим силам, принимает предложения социума и щедро делится своими достижениями. В отрицательном же случае существует риск упустить возможности, избегать момента обмена с миром и быть в состоянии безразличия. Энергия 10 дана для того, чтобы человек мог использовать подсказки вселенной и применять удачу во благо, но не забывающая о важности делиться данной ему удачей.\n\n2. Портрет личности: Энергия 26\nЭнергия 26 обозначает личные качества, которые связаны с интуитивным восприятием и высокой чувствительностью ко всему окружающему. Люди с этой энергией стремятся пребывать в гармонии с окружающим миром. Их жизненный путь тесно связан с обретением душевного равновесия и умением строить глубокие межличностные связи. Они проявляют себя как миротворцы, способные успокаивать конфликты через понимание и сострадание, стремясь к гармонии и балансу во всем.\n\n3. Высшая суть: Внутренний потенциал – Энергия 11, Талант от бога – Энергия 5, Навык прошлого – Энергия 21\nЭнергия 11 показывает на внутреннюю силу и потенциал, которые при разумном использовании помогают человеку чувствовать себя мощным и уверенным. Люди с этой энергией зачастую обладают выдающимися лидерскими качествами и физической выносливостью. Талант от Бога, проявленный через энергию 5, предопределяет умение быть как учеником, так и учителем, готовность передавать знания, уважение к традициям и структурам. Энергия 21 является символом мира и миротворца, напоминает о важности дипломатии и гармоничных отношений, приобретенных в прошлых жизнях. Такой человек умеет устанавливать мир и согласие, находить компромиссы и вдохновлять окружающих на спокойное сосуществование.\n\n---\n\nПредназначение:\n\n1. Личное предназначение: энергия 19\nЭнергия 19 воплощает идею процветания и изобилия. Это энергия жизненной силы, солнечного сияния и оптимизма. Человеку с этой энергией важно стремиться к раскрытию своего внутреннего света и делиться им с окружающими. Успех, богатство и процветание приходят к этому человеку, когда он выбирает путь щедрости и радости. Это энергия лидерства и смелости, требующая от личности уверенности в себе и позитивного мышления. Человек с этой энергией дарит людям добро и вдохновение через свою жажду жизни и счастья.\n\n2. Социальное предназначение: энергия 11\nВ социальной сфере энергия 11 выражается в обретении силы через гармоничное взаимодействие с окружающим миром. Обладателям этой энергии следует учиться не только демонстрировать свои достижения, но и поддерживать других в их индивидуальном развитии. Социальное предназначение состоит в том, чтобы быть образцом силы и решительности, сохранять внутреннее равновесие и способствовать созданию мирного социума. Важно развивать в себе умение делиться своим потенциалом без давления и агрессии.\n\n3. Духовное предназначение: энергия 3\nДуховное предназначение энергии 3 связано с творчеством, заботой о близких, а также гармонией внутри семьи. Это энергия, призывающая человека к реализации своих художественных стремлений, к построению гармоничных отношений и заботе о других. Человек с этой энергией должен видеть в своей жизни красоту и проявлять её в каждом своем деле. Творческое самовыражение и поддержка родственников станут для него путём к духовному росту.\n\n4. Планетарное предназначение: энергия 14\nЭнергия 14 связана с внутренняя гармонией и умением находить баланс. Планетарная роль этой энергии заключается в духовном служении и гармонизации окружающего пространства. Люди с этой энергией стремятся к сохранению мира и равновесия на планетарном уровне, вдохновляясь проявлениями искусства и творчества. Им важно искать золотую середину в любых начинаниях и делиться этим умением с другими.\n\n---\n\nДетско-родительские отношения:\n\n1. Для чего душа пришла к родителям – энергия 26\nЭнергия 26 в данной позиции указывает на необходимость обрести баланс и гармонию в отношениях с родителями. Душа пришла в эту семью, чтобы научиться любви и взаимопониманию, обрести опыт сострадания и научиться строить глубокие душевные связи. Родители могут играть роль наставников, помогая раскрыть внутреннюю мудрость и понимание органов эмоциональной сферы. Опыт отношений с родителями позволяет человеку научиться управлять своими внутренними ощущениями и интуицией, вырастая в духовной среде, способствующей развитию его истинного \"я\".\n\n2. Задача отношений – энергия 8\nЭнергия 8 подразумевает жизнь в соответствии с законами справедливости и честности. В отношениях с родителями, основная задача заключается в понимании причинно-следственных связей и наработки опыта партнерства на равных. Человек должен стремиться осознавать свои поступки и их последствия, преодолевая родительские установки, которые ограничивают восприятие мира. Гармония в семейных отношениях достигается через ведение честного диалога, взаимоуважение и поддержание эмоционального баланса.\n\n3. Ошибки во взаимоотношениях с родителями и своими детьми – энергия 9\nЭнергия 9 акцентирует внимание на важности построения позитивных межличностных отношений. Часто люди с этой энергией совершают ошибку, сдерживая свои чувства или испытывая страх одиночества, что приводит к изоляции и непониманию в отношениях. Основная задача – научиться доверять окружающим, готовность открываться эмоциям и делиться знаниями. Это позволяет создать благоприятную атмосферу для роста и развития в семье, где преобладает понимание и поддержка.\n\n---\n\nТаланты:\n\n1. Талант от бога – энергия 5\nЭнергия 5 раскрывает талант учителя, способность передавать знания и обучаться новым. Этот талант от Бога подразумевает умение воспринимать духовные учения и структурировать их, следуя традициям и порядку. Люди с этой энергией обладают природной мудростью и тягой к различным формам образования, что позволяет им достигать успеха через обучение и наставничество. Проявляя этот талант, человек может влиять на другие, предоставляя своему окружению возможность для роста и развития.\n\n2. Внутренний потенциал: энергия 11\nЭнергия 11 символизирует мощное внутреннее ядро и потенциал, способное воплотить в жизнь многие замыслы. Люди, наделенные этой энергией, имеют огромную внутреннюю силу, которая помогает им добиваться поставленных целей даже в условиях интенсивной работы. Использование этого потенциала требует осознания своей силы и способности восстанавливать энергию путем поиска баланса между трудом и отдыхом.\n\n3. Навык прошлого: энергия 21\nЭнергия 21 указывает на наличие миротворческого навыка из прошлого. Человек с этой энергией умеет создавать гармонию и мир вокруг себя, он обладает дипломатическими навыками и стремится к обозначению нового мира. Этот навык позволяет находить подходы к решению конфликтов или споров, способствуя созданию сбалансированных и поддерживающих отношений на всех уровнях жизни.\n\n---\n\nРодовые программы:\n\n1. Духовные задачи – энергии 10, 15\nЭнергия 10 в духовных задачах подчеркивает важность доверия высшим силам и нахождения в потоке. Это предполагает умение принимать жизнь, её циклы и возможности с благодарностью и открытым сердцем. Энергия 15 указывает на проработку теневых сторон, принятие внутренних противоречий и стремление к воссоединению с внутренним ядром. Оба аспекта направлены на понимание себя, нахождение гармонии между светом и тенью, что способствует духовному росту и прогрессу.\n\n2. Материальные задачи – энергии 4, 9\nЭнергия 4 в материальных задачах представляет лидерство и установление стабильности. Люди с этой энергией должны учиться наращивать материальные ресурсы через разумное управление и твердую ответственность. Энергия 9, напротив, фокусируется на том, чтобы вести материалистическую часть жизни с мудростью, подавать знания, не зацикливаясь на материальных предметах как таковых. Она учит человека не бояться одиночества, а искать поддержку в глубоких знаниях и взаимопонимании.\n\n---\n\nКармический хвост:\n\nКармический хвост: Энергии 15, 20, 5\nЭнергия 15 указывает на необходимость просмотра своих теневых сторон, проработки искушений и привычек, что мешает духовному развитию. Это шанс обрести понимание полной интеграции своих аспектов личности. Энергия 20 подчеркивает важность связи с предками и родом, обучения из семьи и поддержки, которая может прийти оттуда. Энергия 5 добавляет аспект учения и учительства, делая акцент на честности и духовной мудрости, этот аспект призывает охлаждать свой ум, проявлять высокую дисциплину и порядочность. Объединение этих энергий предлагает пройти путь очищения через принятие и обучение, осваивая кармические уроки и преодолевая предыдущие неудачи."
        # while response_text is None and attempt < max_retries:
        #     attempt += 1
        #     response_text = await generate_gpt_response(user_name, values)
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

    if category == "Неизвестная категория":
        await callback_query.message.answer("Категория не найдена. Пожалуйста, выберите другую.")
        readings_left += 1
        return

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
