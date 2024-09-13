# handlers/sections_handler.py

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from openai import AsyncOpenAI

import config
from keyboards.back_to_menu import create_back_button
from keyboards.sections_fate_matrix import create_sections_keyboard, functions_keyboard
from services.birthday_service import calculate_values
from services.message_service import delete_messages, send_initial_messages
from states import QuestionState

router = Router()

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def handle_section(callback_query: CallbackQuery, state: FSMContext, category: str):
    data = await state.get_data()

    categories_dict = data.get("full_response", {})
    selected_category = categories_dict.get(category, "Неизвестная категория")

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
        "section_family_relationships": "Детско-родительские отношения",
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

    await callback_query.message.answer(selected_category, reply_markup=create_back_button())

@router.callback_query(lambda callback: callback.data == "go_back_to_categories")
async def handle_back_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    data = await state.get_data()
    first_message_id = data.get("first_message_id")
    question_prompt_message_id = data.get("question_prompt_message_id")

    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])

    section_message = "Ура, ваша матрица судьбы готова 🔮\n\nВы можете посмотреть расклад по каждому из разделов.\n✅ - доступно бесплатно\n🔐 - требуется полный доступ"
    question_message = ("Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
                        " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
                        "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)")

    await send_initial_messages(callback_query.bot, callback_query.message.chat.id, state, section_message, question_message, create_sections_keyboard(), functions_keyboard())
