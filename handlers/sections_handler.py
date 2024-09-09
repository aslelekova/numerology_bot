# handlers/sections_handler.py

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from openai import AsyncOpenAI

import config
from keyboards.back_to_menu import create_back_button
from keyboards.sections_fate_matrix import create_sections_keyboard
from services.birthday_service import calculate_values
from services.gpt_service import generate_gpt_response, EventHandler
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

async def handle_section(callback_query: CallbackQuery, state: FSMContext):

    data = await state.get_data()


    categories_dict = data.get("full_response", {})
    print(categories_dict)


    category_key = callback_query.data
    selected_category = categories_dict.get(category_key, "Неизвестная категория")

    if selected_category == "Неизвестная категория":
        await callback_query.message.answer("Категория не найдена. Пожалуйста, выберите другую.")
        return


    await callback_query.message.answer(selected_category, reply_markup=create_back_button())


@router.callback_query(lambda callback: callback.data.startswith("section_"))
async def handle_section_callback(callback_query: CallbackQuery, state: FSMContext):
    category_mapping = {
        "section_personal": "Личные качества",
        "section_destiny": "Предназначение",
        "section_talents": "Таланты",
        "section_family_relationships": "Детско родительские отношения",
        "section_generic_programs": "Родовые программы",
        "section_karmic_tail": "Кармический хвост",
        "section_karmic_lesson": "Главный кармический урок",
        "section_relationships": "Отношения",
        "section_money": "Деньги",
    }

    category_key = callback_query.data
    category = category_mapping.get(category_key, "Неизвестная категория")

    if category == "Неизвестная категория":
        await callback_query.message.answer("Категория не найдена. Пожалуйста, выберите другую.")
        return

    data = await state.get_data()
    response_text = data.get("full_response", {})

    if not isinstance(response_text, dict):
        await callback_query.message.answer("Произошла ошибка при обработке данных. Пожалуйста, повторите попытку.")
        return

    selected_category = response_text.get(category, "Неизвестная категория")

    if selected_category == "Неизвестная категория":
        await callback_query.message.answer("Категория не найдена. Пожалуйста, выберите другую.")
        return

    first_message_id = data.get("first_message_id")
    question_prompt_message_id = data.get("question_prompt_message_id")

    if first_message_id:
        try:
            await callback_query.message.chat.delete_message(message_id=first_message_id)
        except Exception as e:
            print(f"Ошибка при удалении первого сообщения: {e}")

    if question_prompt_message_id:
        try:
            await callback_query.message.chat.delete_message(message_id=question_prompt_message_id)
        except Exception as e:
            print(f"Ошибка при удалении второго сообщения: {e}")

    await callback_query.message.answer(selected_category, reply_markup=await create_back_button(callback_query, state))



@router.callback_query(lambda callback: callback.data == "go_back_to_categories")
async def create_back_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

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

    question_prompt_message = await callback_query.message.answer(
        "Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
        " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
        "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)",
        reply_markup=inline_keyboard,
        parse_mode="HTML"
    )
    await state.update_data(question_prompt_message_id=question_prompt_message.message_id)
