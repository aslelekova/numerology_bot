from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from openai import AsyncOpenAI

import config
from keyboards.back_to_menu import create_back_button
from keyboards.sections_fate_matrix import create_sections_keyboard
from services.gpt_service import generate_gpt_response
from states import QuestionState

router = Router()

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


@router.callback_query(lambda callback: callback.data == "get_full_access")
async def handle_full_access(callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Тариф 1 (290 руб.)", callback_data="tariff_1")],
            [InlineKeyboardButton(text="Тариф 2 (490 руб.)", callback_data="tariff_2")],
            [InlineKeyboardButton(text="Тариф 3 (790 руб.)", callback_data="tariff_3")]
        ]
    )

    await callback_query.message.answer(
        "Тариф 1. \n- 5 раскладов (любых) \n- 10 вопросов \n💲 290 рублей\n\n"
        "Тариф 2.\n- 8 раскладов (любых)\n- 20 вопросов\n💲 490 рублей\n\n"
        "Тариф 3.\n- 15 раскладов (любых)\n- 40 вопросов\n💲 790 рублей",
        reply_markup=keyboard
    )

async def handle_section(callback_query: CallbackQuery, state: FSMContext, category: str):
    # Получаем данные из состояния
    data = await state.get_data()

    # Удаляем предыдущее сообщение с категориями
    first_message_id = data.get("first_message_id")
    if first_message_id:
        try:
            await callback_query.bot.delete_message(callback_query.message.chat.id, first_message_id)
        except Exception as e:
            print(f"Error deleting first message with ID {first_message_id}: {e}")

    # Удаляем предыдущее сообщение с предложением задать вопрос
    second_message_id = data.get("second_message_id")
    if second_message_id:
        try:
            await callback_query.bot.delete_message(callback_query.message.chat.id, second_message_id)
        except Exception as e:
            print(f"Error deleting second message with ID {second_message_id}: {e}")

    # Создаем новое сообщение
    generating_message = await callback_query.message.answer("⏳")

    # Генерация текста ответа
    response_text = await generate_gpt_response(data.get("user_name"), data.get("user_date"), category)

    # Удаляем сообщение с индикатором загрузки
    await generating_message.delete()

    # Отправляем ответ и сохраняем ID сообщения
    first_message = await callback_query.message.answer(response_text, reply_markup=create_back_button())
    await state.update_data(first_message_id=first_message.message_id)

    # Создаем inline-клавиатуру и новое сообщение с предложением задать вопрос
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить полный доступ", callback_data="get_full_access")],
        [InlineKeyboardButton(text="Задать бесплатный вопрос", callback_data="ask_free_question")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ])

    second_message = await callback_query.message.answer(
        "Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
        " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
        "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с "
        "партнером?</b>)",
        reply_markup=inline_keyboard,
        parse_mode="HTML"
    )

    # Сохраняем ID второго сообщения
    await state.update_data(second_message_id=second_message.message_id)

    # Обновляем список ID сообщений, которые нужно удалить при нажатии на "Главное меню"
    await state.update_data(previous_message_ids=[first_message.message_id, second_message.message_id])

@router.callback_query(lambda callback: callback.data.startswith("section_"))
async def handle_section_callback(callback_query: CallbackQuery, state: FSMContext):
    free_categories = {
        "section_personal": "Личные качества",
        "section_destiny": "Предназначение",
        "section_family_relationships": "Детско родительские отношения",
        "section_talents": "Таланты",
    }

    category_mapping = {
        "section_personal": "Личностные качества",
        "section_destiny": "Предназначение",
        "section_talents": "Таланты",
        "section_family_relationships": "Детско родительские отношения",
        "section_generic_programs": "Родовые программы",
        "section_karmic_tail": "Кармический хвост",
        "section_karmic_lesson": "Главный кармический урок",
        "section_relationships": "Отношения",
        "section_money": "Деньги",
        "section_definition_of_castes": "Определение каст"
    }

    category = category_mapping.get(callback_query.data, "Неизвестная категория")

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
                    print(f"Error deleting previous warning message: {e}")

        warning_message = await callback_query.message.answer(
            "Эта категория доступна только в платной версии. Пожалуйста, откройте полный доступ."
        )
        await state.update_data(previous_warning_message_id=warning_message.message_id)
        return

    await handle_section(callback_query, state, category)


@router.callback_query(lambda callback: callback.data == "go_back_to_categories")
async def go_back_to_categories(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    first_message_id = data.get("first_message_id")
    question_prompt_message_id = data.get("question_prompt_message_id")

    if first_message_id:
        try:
            await callback_query.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=first_message_id
            )
        except Exception as e:
            print(f"Error deleting current message: {e}")

    if question_prompt_message_id:
        try:
            await callback_query.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=question_prompt_message_id
            )
        except Exception as e:
            print(f"Error deleting question prompt message: {e}")

    sections_keyboard = create_sections_keyboard()
    first_message = await callback_query.message.answer(
        "Ура, ваша матрица судьбы готова 🔮\n\n"
        "Вы можете посмотреть расклад по каждому из разделов.\n"
        "✅ - доступно бесплатно\n"
        "🔐 - требуется полный доступ",
        reply_markup=sections_keyboard
    )

    await state.update_data(first_message_id=first_message.message_id)

    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить полный доступ", callback_data="get_full_access")],
        [InlineKeyboardButton(text="Задать бесплатный вопрос", callback_data="ask_free_question")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ])

    second_message = await callback_query.message.answer(
        f"Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
        " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
        "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с "
        "партнером?</b>)",
        reply_markup=inline_keyboard,
        parse_mode="HTML"
    )

    await state.update_data(second_message_id=second_message.message_id)
