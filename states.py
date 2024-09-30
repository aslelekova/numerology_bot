# states.py
from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    waiting_for_name = State()
    waiting_for_data = State()
    waiting_for_name_num = State()
    waiting_for_data_num = State()
    waiting_for_name_first = State()
    waiting_for_data_first = State()
    waiting_for_name_second = State()
    waiting_for_data_second = State()


class QuestionState(StatesGroup):
    waiting_for_question = State()
    question_asked = State()


class UserState(StatesGroup):
    response_text = State() 