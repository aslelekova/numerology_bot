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
from services.gpt_service import EventHandler, generate_gpt_response
from services.message_service import delete_messages
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
        response_text = "1. Личностные качества:\n\n- Характер человека: Энергия 7. Главная черта этого характера — постоянное стремление к совершенствованию и высокие амбиции. Индивид с таким характером не боится трудностей и готов преодолевать препятствия на пути к своей цели. Однако важно учиться справляться с конфликтами и избегать агрессии, иначе энергия будет расходоваться чрезмерно. Используйте коллектив и семью для реализации своих целей, так как это создаст прочную основу для достижения успеха.\n\n- Портрет личности: Энергия 22. Энергия 22 в портрете личности указывает на врожденные творческие способности и тягу к новым знаниям. Эти люди обычно являются прирожденными исследователями, способными адаптироваться к любым изменениям. Личности этой энергии нужно находиться в постоянном движении, искать новые возможности для саморазвития и избегать затянутости в рутину. Взаимодействуя с окружающими через призму своей внутренней энергии, они приносят не только радость, но и пользу.\n\n- Высшая суть: Внутренний потенциал – Энергия 2, Талант от бога – Энергия 11, Навык прошлого – Энергия 9. Потенциал 2 энергии раскрывает умение быть посредником, дипломатом и хранителем мудрости. 11 энергия отмечает врожденную силу и харизму, которые при правильном подходе дают огромную энергию для созидания и реализации мечт. 9 энергия связывает с прошлым опытом, где были получены знания и понимание, важные для передачи и обучения других. Эти энергии показывают жизненно важные уроки, которые нужно усвоить для достижения гармонии и вдохновения.\n\n---\n\n2. Предназначение:\n\n- Личное предназначение: Энергия 16. Данные энергии указывают на необходимость учиться на разрушениях и видеть в сложных ситуациях возможность для роста. Это внутренняя работа над собой, которая требует не привязываться к материальным веществам и стремиться к глубокому пониманию духовных законов.\n\n- Социальное предназначение: Энергия 5. Эта энергия ориентирует на передачу знаний и укрепление связей с окружающими. Вы находитесь в процессе формирования системы ценностей и учитесь сотрудничать с окружающими, уравновешивая личные и общественные интересы.\n\n- Духовное предназначение: Энергия 21. Указывает на важность большого плана и открытости к новому. Данная энергия символизирует глобальные изменения и эксперименты, при которых вы понемногу расширяете свои границы и способствуете духовному развитию.\n\n- Планетарное предназначение: Энергия 8. Поставьте целью понимание законов причинно-следственных связей и честное взаимодействие с миром. Эта энергия подталкивает к пересмотру родительских установок и искреннему исполнению высшего закона справедливости, делая вклад в гармонизацию планеты. \n\n---\n\n3. Детско-родительские отношения:\n\n- Для чего душа пришла к родителям – энергия 22. Душа пришла в этот мир, чтобы привнести радость и внутреннюю свободу. Она обладает необходимыми ресурсами для поиска нового и необычного. Важно, чтобы эти качества были правильным образом реализованы и использованы для расширения личных и духовных горизонтов. \n\n- Задача отношений – энергия 6. Влияние этой энергии способствует гармонизации и укреплению семейных связей. Она учит искусству несения ответственности за свои решения и строит основу для здоровых, честных и искренних отношений. Детско-родительская связь здесь глубока и символизирует симбиоз, в котором потребности учитываются и поддерживаются. \n\n- Ошибки во взаимоотношениях с родителями и своими детьми – энергия 11. Эта энергия акцентирует внимание на необходимости избегать агрессии и зависимости от покровителей. Она требует учиться делиться энергией и уважать свободу выбора, не допуская чрезмерного давления и взращивая уверенность через созидательное отношение.\n\n---\n\n4. Таланты:\n\n- Талант от бога – энергия 11. Способность вдохновлять и влиять на окружающих, трансформируя агрессию в созидание. Это дар, открывающий двери для огромных свершений и успеха, особенно если сексуальность и внутренняя харизма применены в правильном русле.\n\n- Внутренний потенциал: энергия 2. Это дар дипломатии и способность служить посредником, улавливая и донося информацию, особенно в трудных ситуациях. Развивая эти навыки, можно стать неоценимым мостиком между людьми и событиями.\n\n- Навык прошлого: энергия 9. Знания и опыт, приобретенные в прошлой жизни, позволяют быть лидером мнений и учителем. Человек с такой энергией обычно обладает мудростью и понимает ценность передачи опыта другим, укореняя знания.\n\n---\n\n5. Родовые программы:\n\n- Духовные задачи – энергии 6 и 13. Уроки любви и принятия перемен. Выстраивание гармонических отношений, где уважение к выбору и людям, а также открытость к трансформациям создают основу понимания и поддержки.\n\n- Материальные задачи – энергии 3 и 19. Реализация в социальных и финансовых условиях с акцентом на щедрость и харизму. Необходимо развивать лидерские качества и использовать талант для управления, чтобы прийти к материальному и духовному благополучию.\n\n---\n\n6. Кармический хвост: Энергии 15, 5, 8\n\nКармический хвост отождествляется с задачами, не решенными в прошлом, и современное воплощение требует их проработки. Проработка этих энергий позволяет избавиться от эмоциональных и духовных долгов, улучшая личное восприятие и жизненный путь. Процесс требует осознания и честности с самим собой и другими для установления гармонии и покоя.\n\n---\n\n7. Главный кармический урок души – энергия 8\n\nКармический урок, который предстоит усвоить — это обнаружение и баланс между справедливостью и честностью. Это урок о важности интеграции душевного спокойствия и зрелости, осознание влияния прошлого и привнесение этого опыта в позитивные перспективы.\n\n---\n\n8. Отношения:\n\n- Отношения в прошлом: энергия 15. Прошлый опыт в сфере отношений указывает на возможность повторения старых шаблонов, основанных на манипуляции и контроле. Понимание своих привычек поможет избегать ошибок и проводить работу над собой для улучшения качества взаимодействия с миром.\n\n- Как отношения влияют на финансы: энергия 6. Взаимосвязь между отношениями и финансовым состоянием показывает важность честности и взаимопонимания как основы финансового благополучия. Развивая доверие в отношениях, можно гармонизировать и финансовый поток.\n\n- Кармические отношения: энергия 21. Оказывает влияние на текущую жизнь, делая акцент на необходимости экспериментов и открытости для создания нового. Эти отношения создают основу для обучения через опыт друг с другом в настоящем воплощении.\n\n---\n\n9. Деньги:\n\n- Как заработали деньги в прошлом – Энергия 18. В прошлом воплощении зарабатывание средств происходило через уникальные и необычные подходы. Для достижения финансовой устойчивости требуется вывести эту энергию в положительный аспект, применяя творческие и непринужденные методы, которые будут поддерживать рост.\n\n- Дополнительные возможности – энергия 6. Потенциал увеличения финансового потока заключен в развитии совместной работы и бескорыстного вклада в общее дело. При правильной проработке это может стать значимой опорой для финансовой независимости.\n\n- Сферы высокого финансового потока – энергия 6. Основные направления для создания мощного финансового потока связаны с социальной реализацией и вниманием к окружению. Знание основ взаимодействия с окружающими поможет установить прочные и плодотворные связи в деловой сфере.')"
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
    free_categories = {
        "section_personal": "Личные качества",
        "section_destiny": "Предназначение",
        "section_talents": "Таланты",
        "section_family_relationships": "Детско-родительские отношения",
    }

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

    if callback_query.data not in free_categories:
        warning_message = await callback_query.message.answer(
            "Эта категория доступна только в платной версии. Пожалуйста, откройте полный доступ."
        )
        await state.update_data(previous_warning_message_id=warning_message.message_id)
        return

    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])
    await handle_section(callback_query, state, category)


@router.callback_query(lambda callback: callback.data.startswith("section_full_"))
async def handle_full_section_callback(callback_query: CallbackQuery, state: FSMContext):
    print(f"Received callback_data: {callback_query.data}")
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

    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])
    await handle_section(callback_query, state, category)



async def get_subscription_details(user_id: int):
    conn = sqlite3.connect('users.db') 
    cursor = conn.cursor()
    
    cursor.execute("SELECT subscription_active, readings_left, questions_left FROM login_id WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return {
            "subscription_active": bool(result[0]),
            "readings_left": result[1],
            "questions_left": result[2]
        }
    return {
        "subscription_active": False,
        "readings_left": 0,
        "questions_left": 0
    }