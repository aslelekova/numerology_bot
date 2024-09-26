# services/question_service.py
from aiogram.fsm.context import FSMContext
from services.gpt_service import client


async def generate_question_response(question: str, user_name: str, birth_date: str, state: FSMContext) -> str:
    user_data = await state.get_data()
    response_text = user_data.get('response_text')
    prompt = (
        f"Меня зовут {user_name}, моя дата рождения {birth_date}. "
        f"Я хочу задать следующий вопрос: {question}. Ответь на него на основе расклада {response_text}, "
        f"и постарайся, чтобы ответ был не длиннее 600 символов."
    )
    
    response_text = await generate_response(prompt)
    return response_text


async def generate_response(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    
    response = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o-2024-08-06"
    )
    
    return response.choices[0].message.content


async def generate_suggestions(user_question: str) -> str:
    suggestion_prompt = (
        f"Предложи три новых вопроса, основанных на вопросе пользователя: '{user_question}'. "
        f"Каждый вопрос должен быть пронумерован такой комбинацией \"- 🔮\""
        f"Каждый вопрос начинается с новой строки."
        f"Старайся, чтобы вопросы были ясными и логичными."
    )

    messages = [{"role": "user", "content": suggestion_prompt}]
    

    suggestion_response = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o-2024-08-06",
        max_tokens=150
    )
    
    return suggestion_response.choices[0].message.content
