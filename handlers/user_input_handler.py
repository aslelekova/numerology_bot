# handlers/user_input_handler.py

from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

from calendar_module.calendar_utils import get_user_locale
from calendar_module.schemas import DialogCalendarCallback
from keyboards.sections_fate_matrix import create_sections_keyboard, create_reply_keyboard
from services.calendar_service import process_calendar_selection, start_calendar
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

        data = await state.get_data()
        date_prompt_message_id = data.get("date_prompt_message_id")
        if date_prompt_message_id:
            try:
                await callback_query.bot.delete_message(chat_id=callback_query.message.chat.id,
                                                        message_id=date_prompt_message_id)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")

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
