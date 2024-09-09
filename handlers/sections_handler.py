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


@router.callback_query(DialogCalendarCallback.filter())
async def process_selecting_category(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await process_calendar_selection(callback_query, callback_data)

    if selected:
        user_name, _ = await get_user_data(state)
        await update_user_date(state, date)

        # Генерация значений матрицы судьбы
        day, month, year = date.day, date.month, date.year
        values = calculate_values(day, month, year)

        # Генерация полного ответа с помощью GPT
        handler = EventHandler()
        response_text = await generate_gpt_response(user_name, values, handler)

        # Разделяем сгенерированный текст по категориям
        split_text = response_text.split("---")
        categories = [
            "Личные качества",
            "Предназначение",
            "Таланты",
            "Детско-родительские отношения",
            "Родовые программы",
            "Кармический хвост",
            "Главный кармический урок",
            "Отношения",
            "Деньги"
        ]
        
        categories_dict = {category: split_text[i].strip() for i, category in enumerate(categories) if i < len(split_text)}

        await state.update_data(full_response=categories_dict)

        # Отправляем сообщение о готовности матрицы судьбы
        sections_keyboard = create_sections_keyboard()
        first_message = await callback_query.message.answer(
            "Ура, ваша матрица судьбы готова 🔮\n\n"
            "Вы можете посмотреть расклад по каждому из разделов.\n"
            "✅ - доступно бесплатно\n"
            "🔐 - требуется полный доступ",
            reply_markup=sections_keyboard
        )
        await state.update_data(first_message_id=first_message.message_id)


@router.callback_query(lambda callback: callback.data.startswith("section_"))
async def handle_section_callback(callback_query: CallbackQuery, state: FSMContext):
    free_categories = {
        "section_personal": "Личные качества",
        "section_destiny": "Предназначение",
        "section_family_relationships": "Детско-родительские отношения",
        "section_talents": "Таланты",
    }

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
        print(f"Error: Category '{callback_query.data}' not found.")
        await callback_query.message.answer("Категория не найдена. Пожалуйста, выберите другую.")
        return

    # Проверяем доступ к категории
    if category_key not in free_categories:
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

    # Извлекаем текст из сохраненного ответа
    data = await state.get_data()
    full_response = data.get("full_response", {})
    selected_category_text = full_response.get(category, "Текст по данной категории не найден.")

    await callback_query.message.answer(selected_category_text, reply_markup=create_back_button())
