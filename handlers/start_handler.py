# handlers/start_handler.py
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.handlers import callback_query

from keyboards.main_menu_keyboard import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    user_name = user_data.get("user_name") or message.from_user.first_name

    await state.clear()

    await message.answer(f"Добрый день, {user_name}!\n\nМы рады помочь вам с расчетом матрицы судьбы, нумерологии, "
                         "совместимости, карьерного успеха, богатства и других вопросов.\n\n<b>После каждого расчета вы"
                         "сможете задать любой вопрос.</b> С чего начнем?", reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def handle_help(message: types.Message):
    """
    Handle the /help command to provide information about available commands and how to use the bot.

    :param message: The message object.
    :return: None
    """
    await message.answer(text=(
        "🔮Этот бот предназначен для того, чтобы помочь вам узнать больше о нумерологии и матрице судьбы. "
        "С его помощью вы можете исследовать, как числа влияют на вашу жизнь, и получить полезные советы и "
        "прогнозы.\n\n"
        "🔹 <b>Доступные команды:</b>\n\n"
        "/start - Начать взаимодействие с ботом. Отправляет приветственное сообщение и предлагает начать "
        "работу.\n\n"
        "/help - Получить информацию о доступных командах и узнать, как пользоваться ботом.\n\n"
    )
    )
# handlers/start_handler.py
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from keyboards.main_menu_keyboard import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_name = message.from_user.first_name

    await state.clear()

    await message.answer(f"Добрый день, {user_name}!\n\nМы рады помочь вам с расчетом матрицы судьбы, нумерологии, "
                         "совместимости, карьерного успеха, богатства и других вопросов.\n\n<b>После каждого расчета вы"
                         "сможете задать любой вопрос.</b> С чего начнем?", reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def handle_help(message: types.Message):
    """
    Handle the /help command to provide information about available commands and how to use the bot.

    :param message: The message object.
    :return: None
    """
    await message.answer(text=(
        "🔮Этот бот предназначен для того, чтобы помочь вам узнать больше о нумерологии и матрице судьбы. "
        "С его помощью вы можете исследовать, как числа влияют на вашу жизнь, и получить полезные советы и "
        "прогнозы.\n\n"
        "🔹 <b>Доступные команды:</b>\n\n"
        "/start - Начать взаимодействие с ботом. Отправляет приветственное сообщение и предлагает начать "
        "работу.\n\n"
        "/help - Получить информацию о доступных командах и узнать, как пользоваться ботом.\n\n"
    )
    )
