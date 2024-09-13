# handlers/payment_handler.py

from aiogram.fsm.context import FSMContext

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.sections_fate_matrix import create_sections_keyboard, functions_keyboard


router = Router()

@router.callback_query(lambda callback: callback.data == "get_full_access")
async def handle_full_access(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
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

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="290 руб", callback_data="tariff_1")],
            [InlineKeyboardButton(text="450 руб", callback_data="tariff_2"),
             InlineKeyboardButton(text="650 руб", callback_data="tariff_3")],
             [InlineKeyboardButton(text="Назад", callback_data="back")]
        ]
    )

    await callback_query.message.answer(
        "Мы подготовили для тебя 3 тарифа 💫\n\nТариф 1.  290 рублей\n🔮 5 любых раскладов\n⚡️ 10 ответов на любые вопросы \n\nТариф 2.  450 рублей  (популярный)\n🔮 8 любых раскладов\n⚡️ 20 ответов на любые вопросы  \n\nТариф 3. 650 рублей \n🔮 15 любых раскладов\n⚡️ 40 ответов на любые вопросы \n\nВыберите один из тарифов",
        reply_markup=keyboard
    )


@router.callback_query(lambda callback: callback.data == "back")
async def handle_back_button(callback_query: CallbackQuery, state: FSMContext):
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

    three_functions = functions_keyboard()
    question_prompt_message = await callback_query.message.answer(
        f"Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
        " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
        "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)",
        reply_markup=three_functions,
        parse_mode="HTML"
    )
    await state.update_data(question_prompt_message_id=question_prompt_message.message_id)
