# handlers/sections_handler.py

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from openai import AsyncOpenAI

import config
from keyboards.back_to_menu import create_back_button
from keyboards.sections_fate_matrix import create_full_sections_keyboard, create_sections_keyboard, functions_keyboard
from services.birthday_service import calculate_values
from services.db_service import get_subscription_details
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


@router.callback_query(lambda callback: callback.data == "go_back_to_categories")
async def handle_back_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    user_id = callback_query.from_user.id
    subscription_details = await get_subscription_details(user_id)
    subscription_active = subscription_details["subscription_active"]
    readings_left = subscription_details["readings_left"]
    questions_left = subscription_details["questions_left"]

    if subscription_active:
        first_message = await callback_query.message.answer(
            f"У вас осталось:\n🔮 {readings_left} любых раскладов\n⚡️ {questions_left} ответа на любые вопросы",
            reply_markup=create_full_sections_keyboard()
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
        section_message = "Ура, ваша матрица судьбы готова 🔮\n\nВы можете посмотреть расклад по каждому из разделов.\n✅ - доступно бесплатно\n🔐 - требуется полный доступ"
        question_message = ("Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
                            " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
                            "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)")

        await send_initial_messages(callback_query.bot, callback_query.message.chat.id, state, section_message, question_message, create_sections_keyboard(), functions_keyboard())
