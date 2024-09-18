# handlers/user_input_handler.py

from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

from calendar_module.calendar_utils import get_user_locale
from calendar_module.schemas import DialogCalendarCallback
from handlers.sections_handler import handle_section
from handlers.start_handler import cmd_start
from keyboards.sections_fate_matrix import create_sections_keyboard, create_reply_keyboard, functions_keyboard
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
        response_text = "Личные качества:\n\n1. Характер человека: Энергия 4\nЧеловек с энергией 4 обладает ярко выраженным лидерским потенциалом и умением брать на себя ответственность. Благоприятное проявление этой энергии позволяет человеку строить и управлять успешными проектами, занимая высокие руководящие позиции. Главное умение энергией 4 — это способность контролировать все процессы и доводить начатое до конца. Организаторские навыки, логическое мышление и структурность позволяют достигать поставленных целей. Личность с этой энергией стремится к порядку и хозяйственности, но чтобы избежать негативных проявлений, важно уметь переключаться между различными ролями и избегать деспотизма.\n\n2. Портрет личности: Энергия 18\nЭнергия 18 ведет человека к поиску ответов в эзотерике и духовных практиках. Обладатели этой энергии обладают мощной интуицией и талантом материализовать свои мысли. Если использовать эту силу во благо, можно привлечь изобилие и счастье. Однако, нужно избегать страхов и иллюзий, принимая реальность такой, какая она есть. Вода и лунные циклы играют важную роль в жизни таких людей, помогая им очищать и трансформировать энергию.\n\n3. Высшая суть: Внутренний потенциал – Энергия 4, Талант от бога – Энергия 12, Навык прошлого – Энергия 8\nВнутренний потенциал в энергии 4 подчеркивает лидерские способности и умение брать на себя ответственность за результаты работы. Талант от Бога, энергия 12, вдохновляет человека найти свой путь служения людям, одновременно повышая самооценку и предлагая достойную компенсацию за свои усилия. Навык прошлого, энергия 8, учит человека понимать законы кармы, видеть причинно-следственные связи и соблюдать эмоциональное спокойствие. Эти энергии в совокупности поддерживают рост через знание, силу воли и справедливость.\n\n---\n\n2) Предназначение:\n\n1. Личное предназначение: энергия 22\nЭнергия 22 связана с духовной свободой и самостоятельностью. Личное предназначение человека с этой энергией состоит в поиске собственного пути без навязывания чужих мнений. Это путь к самопознанию и внутренней гармонии, в котором важно избегать экстремизма и придерживаться балансированного подхода к жизни.\n\n2. Социальное предназначение: энергия 8\nСоциальное предназначение подразумевает честность и справедливость. Человек с 8 энергией должен изучать кармические законы и следовать им, принимая существующую реальность. Необходимо сохранять баланс, избегая ненужных битв за справедливость, тем самым создавая мир и гармонию вокруг себя.\n\n3. Духовное предназначение: энергия 3\nЭнергия 3 представляет необходимость быть творцом своей жизни. Духовное предназначение подразумевает использование творческих способностей и ресурсов для достижения внутреннего роста и гармонии. Важно доверять своим интуитивным решениям и не бояться демонстрировать свои таланты во внешнем мире.\n\n4. Планетарное предназначение: энергия 11\nЭнергия 11 связана с раскрытием внутренней силы и потенциала. Планетарное предназначение требует от человека работы над агрессией и использованию силы исключительно для созидания. Важно взаимодействовать с окружающим миром экологично, создавая вокруг себя гармоничную среду и привносить в повседневную жизнь собранность и гармонию.\n\n---\n\n3) Детско-родительские отношения:\n\n1. Для чего душа пришла к родителям: энергия 18\nЭнергия 18 вдохновляет человека на осознание и проработку своих страхов и иллюзий. Она подталкивает к пониманию магических и духовных аспектов бытия, что, в свою очередь, способствует трансформации и личностному росту. Взаимодействие с родителями способствует обретению внутреннего стержня через принятие и понимание глубоких внутренние процессов.\n\n2. Задача отношений: энергия 4\nЭнергия 4 предписывает выстраивание отношений на базе ответственности и лидерства. Взаимодействие с родителями требует умения брать на себя ответственность за собственные действия и поступки. Это предполагает совместную работу и организацию семейных процессов таким образом, чтобы достичь гармонии и порядка в отношениях.\n\n3. Ошибки во взаимоотношениях с родителями и своими детьми: энергия 22\nЭнергия 22 в этом контексте указывает на важность избегания деспотизма и излишнего контроля. Ошибки возникают, когда человек навязывает свои мнения и не позволяет другим свободно выражать себя. Важно поддерживать сбалансированные отношения и уважать индивидуальные границы друг друга.\n\n---\n\n4) Таланты:\n\n1. Талант от бога: энергия 12\nЭнергия 12 способствует раскрытию внутреннего потенциала через служение и помощь другим. Талант этой энергии заключается в способности поддерживать и вдохновлять окружающих, находя пути служения и личного роста. Реализация этого дара может привести к успеху не только в профессиональной сфере, но и в межличностных взаимоотношениях.\n\n2. Внутренний потенциал: энергия 4\nЭнергия 4 проявляется в лидерских качествах и стремлении к порядку и организации. Внутренний потенциал данной энергии заключается в способности вести за собой и инициировать изменения. Это энергия действия, в рамках которой важно работать над саморазвитием и стараться избегать деструктивного контроля над окружающими.\n\n3. Навык прошлого: энергия 8\nЭнергия 8 выводит человека на путь понимания справедливости и кармических законов. Навык прошлого помогает строить честные и открытые отношения, опираясь на опыт и справедливость. Это энергия, дающая возможность видеть причинно-следственные связи и использовать их для планирования успешного будущего.')"
        # response_text = await generate_gpt_response(user_name, values)
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
        data = await state.get_data()
        previous_warning_message_id = data.get("previous_warning_message_id")
        if previous_warning_message_id:
            try:
                await callback_query.bot.delete_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=previous_warning_message_id
                )
            except Exception as e:
                if "message to delete not found" not in str(e):
                    print(f"Ошибка при удалении предыдущего сообщения о платной категории: {e}")

        warning_message = await callback_query.message.answer(
            "Эта категория доступна только в платной версии. Пожалуйста, откройте полный доступ."
        )
        await state.update_data(previous_warning_message_id=warning_message.message_id)
        return

    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])
    await handle_section(callback_query, state, category)
