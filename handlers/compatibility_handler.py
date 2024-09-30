# handlers/compatibility_handler.py

from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from start_handler import cmd_start
from states import Form
from aiogram.filters.state import StateFilter

router = Router()


@router.callback_query(F.data == "compatibility")
async def handle_compatibility(call: CallbackQuery, state: FSMContext):
    await state.update_data(category='compatibility')

    message_text = "✍️ Введите имя первого человека:"
    await prompt_for_name_first(call, state, message_text)

async def prompt_for_name_first(call: CallbackQuery, state: FSMContext, message_text: str):
    await call.message.delete()
    prompt_message = await call.message.answer(message_text)
    await state.update_data(prompt_message_id=prompt_message.message_id)
    await state.set_state(Form.waiting_for_name_first)

@router.message(StateFilter(Form.waiting_for_name_first))
async def handle_first_name_input(message: types.Message, state: FSMContext):
    first_name = message.text
    await state.update_data(first_name=first_name)

    # Запрашиваем возраст первого человека
    await message.answer("📅 Введите возраст первого человека:")
    await state.set_state(Form.waiting_for_age_first)

@router.message(StateFilter(Form.waiting_for_age_first))
async def handle_first_age_input(message: types.Message, state: FSMContext):
    first_age = message.text
    await state.update_data(first_age=first_age)

    # Запрашиваем имя второго человека
    await message.answer("✍️ Введите имя второго человека:")
    await state.set_state(Form.waiting_for_name_second)

@router.message(StateFilter(Form.waiting_for_name_second))
async def handle_second_name_input(message: types.Message, state: FSMContext):
    second_name = message.text
    await state.update_data(second_name=second_name)

    # Запрашиваем возраст второго человека
    await message.answer("📅 Введите возраст второго человека:")
    await state.set_state(Form.waiting_for_age_second)

@router.message(StateFilter(Form.waiting_for_age_second))
async def handle_second_age_input(message: types.Message, state: FSMContext):
    second_age = message.text
    await state.update_data(second_age=second_age)

    # Здесь вы можете обработать совместимость, используя введенные данные
    data = await state.get_data()
    first_name = data.get("first_name")
    first_age = data.get("first_age")
    second_name = data.get("second_name")
    second_age = data.get("second_age")

    # Логика обработки совместимости, например:
    response_text = f"Совместимость между {first_name} ({first_age} лет) и {second_name} ({second_age} лет)."
    
    await message.answer(response_text)
    await cmd_start(message, state)  # Возвращаемся в главное меню

