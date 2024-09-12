# handlers/user_input_handler.py

from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

from calendar_module.calendar_utils import get_user_locale
from calendar_module.schemas import DialogCalendarCallback
from handlers.start_handler import cmd_start
from keyboards.sections_fate_matrix import create_sections_keyboard, create_reply_keyboard, functions_keyboard
from services.birthday_service import calculate_values
from services.calendar_service import process_calendar_selection, start_calendar
from services.gpt_service import EventHandler, generate_gpt_response
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
        # response_text = await generate_gpt_response(user_name, values, handler)
         response_text = "### Личные качества:\n\n**1. Характер человека: Энергия 12**\n\nЭнергия 12 символизирует человека, который добр и располагает к себе. Он всегда готов прийти на помощь и оказать поддержку, стремится обнять весь мир и делиться душевным теплом. В минусе, такой человек может стать жертвой обстоятельств, требуя к себе постоянного внимания и манипулируя окружающими. Он может также пытаться \"спасать\" других, не спрашивая их разрешения, что приводит к непониманию и конфликтам. Следует научиться говорить \"нет\" и отпускать то, что уже изжило себя, чтобы обрести внутренний баланс и гармонию.\n\n**2. Портрет личности: Энергия 31**\n\nЭнергия 31 отражает личность, наделенную способностью быть в гармонии с собственной душой. Это человек, который ценит индивидуальность и стремится к самовыражению через различные сферы жизни. Он легко общается с окружающими, талантливо реализует свои способности и достигает успеха в выбранных областях. Взаимодействие с миром для него - это возможность испытать удовлетворение и радость от жизни. Такой человек подвержен депрессии, если не может реализовать свои таланты и стремления, наполняя жизнь смыслом и удовольствием.\n\n**3. Высшая суть: Энергия 10, Талант от Бога – Энергия 5, Навык прошлого – Энергия 22**\n\nЭнергия 10 символизирует внутренний потенциал, который открывается при доверии и интуитивных решениях. Талант от Бога, представленный Энергией 5, говорит о важности постоянного обучения и передачи знаний. Это источник вдохновения и движения вперед. Энергия 22, как навык прошлого, показывает, что человек обладает умением создавать и воплощать смелые идеи в реальность. Необходимо использовать этот опыт для позитивных изменений, избегая депрессии и отчаяния.\n\n---\n\n### Предназначение:\n\n**1. Личное предназначение: Энергия 21**\n\nЭнергия 21 связана с глобальным восприятием мира и стремлением к гармонии. Личное предназначение заключается в принятии других людей и культур, интеграции различных взглядов и установлении толерантности. Человек с этой энергией может стать лидером, способным соединить и направить других к общим целям. Важно развивать открытость к изменениям и готовность путешествовать, открывая новые горизонты.\n\n**2. Социальное предназначение: Энергия 6**\n\nЭнергия 6 символизирует гармонию и баланс в отношениях с окружающими. Социальное предназначение включает в себя создание теплых и эстетически приятных взаимодействий с людьми. В минусе, это может проявляться как постоянное недовольство и поиск идеала. Для достижения успеха необходимо научиться принимать людей такими, какие они есть, и стремиться к гармонии в отношениях.\n\n**3. Духовное предназначение: Энергия 9**\n\nЭнергия 9 характеризует духовную зрелость и мудрость. Духовное предназначение включает в себя обучение и передачу сокровенных знаний, создание сообщества единомышленников и поддержание внутреннего мира. Человек с этой энергией должен избегать закрытости и холодности, развивая свою способность к эмпатии и пониманию. Это путь к духовному росту через принятие и осознание своей роли в мире.\n\n**4. Планетарное предназначение: Энергия 15**\n\nЭнергия 15 связана с искушением и сложностями на пути. Планетарное предназначение включает в себя преодоление внутренних и внешних теневых сторон, таких как агрессия, эгоизм и стремление к власти. Человек с этой энергией должен научиться осознавать свою темную сторону и работать на её трансформацию в позитивные качества. Этот процесс помогает достигнуть гармонии внутри себя и поддерживать баланс в окружающем мире.\n\n---\n\n### Детско-родительские отношения:\n\n**1. Для чего душа пришла к родителям: Энергия 31**\n\nЭнергия 31 в контексте родительских отношений указывает на необходимость построения гармоничных взаимосвязей с родителями. Душа пришла, чтобы научиться принимать и почитать своих родителей, работая над собственной индивидуальностью. Это важно для достижения внутренней целостности и для передачи мудрости следующим поколениям. Человек с этой энергией должен стремиться к независимости и выражению своей уникальности через понимание и принятие родовых традиций.\n\n**2. Задача отношений: Энергия 11**\n\nЭнергия 11 символизирует силу и потенциал отношений. Задача взаимодействия с родителями заключается в развитии энергии созидания и мягкости. Родители должны научиться использовать свою силу во благо, не подавляя окружающих, а поддерживая их. Это помогает создать гармоничные отношения, основанные на взаимопонимании и уважении. Проявление агрессии и желание навязать свою волю силой должны быть преодолены.\n\n**3. Ошибки во взаимоотношениях с родителями и своими детьми: Энергия 7**\n\nЭнергия 7 характеризует лидерство и активную жизненную позицию. Основные ошибки в отношениях заключаются в доминировании, склонности навязывать свою волю и постоянных спорах. Это может приводить к конфликтам и недопониманию. Чтобы избежать этих ошибок, необходимо развивать терпимость и умение выслушивать друг друга. Лидерство должно основываться на вдохновении и поддержке, а не на подавлении и критике.\n\n---\n\n### Таланты:\n\n**1. Талант от Бога – Энергия 5**\n\nЭнергия 5 связана с постоянным развитием и обучением. Талант от Бога заключается в умении непрерывно познавать новое и делиться своими знаниями с другими. Это талант учителя и наставника, который вдохновляет других на саморазвитие и рост. Для реализации этого таланта важно избегать навязывания своего мнения и принимать разнообразие мнений и подходов, развивая свою гибкость и открытость.\n\n**2. Внутренний потенциал: Энергия 10**\n\nЭнергия 10 символизирует умение действовать по интуиции и принимать поддержку внешних факторов. Внутренний потенциал раскрывается, когда человек принимает перемены легко и уверенно. Это энергия легкости и оптимизма, с ней человек может смело идти на риск и находить пользу в неопределенности. Главное - не сопротивляться цикличности и учиться быть благодарным за возможности, которые предоставляет жизнь.\n\n**3. Навык прошлого: Энергия 22**\n\nЭнергия 22 указывает на способность создавать и воплощать смелые идеи. В прошлом человек уже развил навык реализации глубоких и значимых проектов. Этот опыт является основой для текущего воплощения, и важно продолжать использовать этот навык с позитивным настроем. Проектирование и материализация задумок - это ключевые аспекты, которые необходимо развивать для достижения успеха и самоудовлетворения.\n\n---\n\n### Родовые программы:\n\n**1. Духовные задачи: Энергии 5, 20**\n\nЭнергия 5 в контексте родовых программ говорит о важности передачи знаний и мудрости от поколения к поколению. Это духовная задача, включающая обучение и наставничество, которое помогает развивать семейные ценности и укреплять родовые связи. Энергия 20 добавляет интуицию и способность к прощению в этот процесс. Она учит принимать своих предков и работать над примирением с прошлым, помогая роду развиваться духовно и поддерживать гармонию в семье.\n\n**2. Материальные задачи: Энергии 10, 16**\n\nЭнергия 10 в материальном аспекте символизирует стремление к легкости и принятие материальных благ с благодарностью. Родовая задача здесь заключается в выработке здорового отношения к богатству и достатку, избегая привязанности к вещам и материальному. Энергия 16 добавляет аспект трансформации, учит принимать перемены и видеть в них возможности для роста и развития. Род должен научиться извлекать выгоду из изменений и использовать их для улучшения благосостояния.\n\n---\n\n### Кармический хвост:\n\n**Кармический хвост: Энергии 18, 6, 6**\n\nЭнергия 18 символизирует прошлые страхи и сомнения, которые переходят в текущее воплощение. Кармический хвост включает задачи по проработке негативных эмоций и внутреннего беспокойства. Две энергии 6 добавляют к этому недовольство в отношениях и стремление к идеалам, что может проявляться как энергетический вампиризм и постоянные конфликты. Шаги к разрешению этих кармических задач включают развитие внутреннего мира и гармонии, а также умение превращать негатив в позитив.\n\n---\n\n### Главный кармический урок души – Энергия 6\n\nЭнергия 6 как главный кармический урок направлена на обретение гармонии и баланса в отношениях. Урок заключается в том, чтобы научиться любить и принимать других без условий. Это включает преодоление склонности к критике и недовольству, а также стремление к эстетике и красоте в жизни. Для успеха необходимо развивать эмпатию и понимание, при этом оставаясь верным себе и своим идеалам.\n\n---\n\n### Отношения:\n\n**1. Отношения в прошлом: Энергия 18**\n\nЭнергия 18 указывает на негативные аспекты прошлых отношений, такие как страхи, сомнения и манипуляции. В прошлых воплощениях это могло проявляться как недоверие и даже использование силы во вред. Важно осознать эти ошибки и работать над их исправлением в текущих отношениях, развивая открытость и доверие к партнёрам, избегая повторения негативных сценариев.\n\n**2. Как отношения влияют на финансы: Энергия 4**\n\nЭнергия 4 символизирует влияние отношений на материальное благополучие. Гармоничные и стабильные взаимоотношения способствуют успешной карьере и финансовой независимости. Однако, конфликты и недопонимания могут привести к финансовым потерям и трудностям. Необходимо развивать в себе лидерские качества и стремиться к честности и стабильности в отношениях, это способствует укреплению финансового потока.\n\n**3. Кармические отношения: Энергия 22**\n\nЭнергия 22 показывает кармическую природу текущих отношений, указывая на важные уроки и задачи, которые необходимо решить. В этих отношениях проявляются прошлые наработки и потенциал для реализации глубоких проектов и идей. Важно использовать этот опыт для позитивных изменений и избегать повторения негативных сценариев, развивая потенциал и реализуя смелые идеи в жизни.\n\n---\n\n### Деньги:\n\n**1. Как заработали деньги в прошлом – Энергия 22**\n\nЭнергия 22 говорит о смелом подходе к финансовой деятельности в прошлом воплощении. При помощи креативности и нестандартных решений человек мог зарабатывать деньги, воплощая свои идеи в реальность. Важно использовать этот опыт в текущей жизни, при этом развивая новый подход и избегая повторения негативных аспектов.\n\n**2. Дополнительные возможности – Энергия 4**\n\nЭнергия 4 символизирует лидерские качества и активный путь к заработку. Дополнительные возможности для увеличения финансового потока включают честность, стабильность и способность быть лидером. Развивая эти качества, человек может достичь успеха и увеличить свой доход.\n\n**3. Сферы высокого финансового потока – Энергия 8**\n\nЭнергия 8 указывает на наиболее благоприятные сферы для высокого финансового потока. Это может быть бизнес, требующий честности, стабильности и доверия. Инвестиции в долгосрочные проекты или области, связанные с большими корпорациями, также могут приносить хороший доход. Важно направлять средства на благотворительные цели и развитие, чтобы поддерживать высокий уровень финансового потока."
        # while response_text is None and attempt < max_retries:
        #     attempt += 1
        #     response_text = await generate_gpt_response(user_name, values)
        #     if not response_text:
        #         print(f"Попытка {attempt}: не удалось сгенерировать ответ.")


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
