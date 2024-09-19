# services/question_service.py
from aiogram.fsm.context import FSMContext
from services.gpt_service import client

async def generate_question_response(question: str, user_name: str, birth_date: str, state: FSMContext) -> str:
    user_data = await state.get_data()
    response_text = user_data.get('response_text')
    prompt = (
        f"Меня зовут {user_name}, моя дата рождения {birth_date}. "
        f"Я хочу задать следующий вопрос: {question}. Ответь на него на основе расклада {response_text}"
    )
    
    response_text = await generate_response(prompt)
    return response_text


async def generate_response(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4o-2024-08-06"
    )
    
    return response.choices[0].message.content


async def generate_suggestions(user_question: str) -> str:
    suggestion_prompt = (
        f"Предложи три вопроса (пронумеруй их так: 🔮 -), разделяй их как \\n, на основе следующего вопроса "
        f"пользователя: '{user_question}'."
    )
    messages = [{"role": "user", "content": suggestion_prompt}]
    

    suggestion_response = client.chat.completions.create(
        messages=messages,
        model="gpt-4o-2024-08-06"
    )
    
    return suggestion_response.choices[0].message.content
