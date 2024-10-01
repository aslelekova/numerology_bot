# services/user_service.py

from aiogram.fsm.context import FSMContext


async def get_user_data(state: FSMContext):
    """
    Retrieves user data from the FSM context.

    :param state: The FSM context from which to retrieve user data.
    :return: A tuple containing the user's name and date, if available.
    """
    data = await state.get_data()
    return data.get('user_name'), data.get('user_date')


async def update_user_name(state: FSMContext, name: str):
    """
    Updates the user's name in the FSM context.

    :param state: The FSM context in which to update the user's name.
    :param name: The new name to set for the user.
    :return: None
    """
    await state.update_data(user_name=name)


async def update_user_date(state: FSMContext, date):
    """
    Updates the user's date in the FSM context.

    :param state: The FSM context in which to update the user's date.
    :param date: The new date to set for the user.
    :return: None
    """
    await state.update_data(user_date=date)

async def update_user_date_com(state: FSMContext, date, partner: str = "first"):
    data = await state.get_data()
    
    if partner == "first":
        # Сохраняем дату для первого партнера
        await state.update_data(date_first_partner=date)
    elif partner == "second":
        # Сохраняем дату для второго партнера
        await state.update_data(date_second_partner=date)
