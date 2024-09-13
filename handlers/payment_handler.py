from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from services.message_service import delete_messages, send_initial_messages
from keyboards.sections_fate_matrix import create_sections_keyboard, functions_keyboard

router = Router()

@router.callback_query(lambda callback: callback.data == "get_full_access")
async def handle_full_access(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    first_message_id = data.get("first_message_id")
    question_prompt_message_id = data.get("question_prompt_message_id")

    await delete_messages(callback_query.bot, callback_query.message.chat.id, [first_message_id, question_prompt_message_id])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="290 руб", callback_data="tariff_1")],
            [InlineKeyboardButton(text="450 руб", callback_data="tariff_2"),
             InlineKeyboardButton(text="650 руб", callback_data="tariff_3")],
             [InlineKeyboardButton(text="Назад", callback_data="back")]
        ]
    )

    await callback_query.message.answer(
        "Мы подготовили для тебя 3 тарифа 💫\n\nТариф 1.  290 рублей\n🔮 5 любых раскладов\n⚡️ 10 ответов на любые вопросы \n\nТариф 2.  450 рублей  (популярный)\n🔮 8 любых раскладов\n⚡️ 20 ответов на любые вопросы \n\nТариф 3.  650 рублей \n🔮 15 любых раскладов\n⚡️ 40 ответов на любые вопросы \n\nВыберите один из тарифов",
        reply_markup=keyboard
    )


@router.callback_query(lambda callback: callback.data == "back")
async def handle_back_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    section_message = "Ура, ваша матрица судьбы готова 🔮\n\nВы можете посмотреть расклад по каждому из разделов.\n✅ - доступно бесплатно\n🔐 - требуется полный доступ"
    question_message = ("Получите <b>ответы на все свои вопросы</b> с ПОЛНЫМ доступом к:\n🔮 Матрице судьбы\n💸 Нумерологии"
                        " | Личному успеху | Финансам\n💕 Совместимости с партнером\n\nИли <b>задайте любой вопрос</b> нашему "
                        "персональному ассистенту и получите мгновенный ответ (например: 💕<b>Как улучшить отношения с партнером?</b>)")
    await send_initial_messages(callback_query.bot, callback_query.message.chat.id, state, section_message, question_message, create_sections_keyboard(), functions_keyboard())
