# states.py
from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    waiting_for_name = State()
    waiting_for_data = State()


class QuestionState(StatesGroup):
    waiting_for_question = State()
    question_asked = State()