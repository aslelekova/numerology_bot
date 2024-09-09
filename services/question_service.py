# services/question_service.py

from services.gpt_service import client

async def generate_question_response(question: str, user_name: str, birth_date: str) -> str:

    prompt = (
        f"Меня зовут {user_name}, моя дата рождения {birth_date}. "
        f"Я хочу задать следующий вопрос: {question}."
    )
    
    response_text = await generate_response(prompt, client)
    
    return response_text


async def generate_response(prompt: str, client) -> str:
    messages = [{"role": "user", "content": prompt}]
    response = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o"
    )
    return response.choices[0].message.content


async def generate_suggestions(user_question: str, client) -> str:
    suggestion_prompt = (
        f"Предложи три вопроса (пронумеруй их так: 🔮 -), разделяй их как \\n, на основе следующего вопроса "
        f"пользователя: '{user_question}'."
    )
    messages = [{"role": "user", "content": suggestion_prompt}]
    suggestion_response = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o"
    )
    return suggestion_response.choices[0].message.content
