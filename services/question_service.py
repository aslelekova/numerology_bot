# services/question_service.py

async def generate_response(prompt: str, client) -> str:
    messages = [{"role": "user", "content": prompt}]
    response = await client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo"
    )
    return response.choices[0].message.content


async def generate_suggestions(user_question: str, client) -> str:
    suggestion_prompt = (
        f"Предложи три вопроса (пронумеруй их так: 🔮 -), разделяй их как \\n, на основе следующего вопроса пользователя: '{user_question}'."
    )
    messages = [{"role": "user", "content": suggestion_prompt}]
    suggestion_response = await client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo"
    )
    return suggestion_response.choices[0].message.content
