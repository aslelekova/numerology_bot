# services/gpt_services.py

from openai import AsyncOpenAI
import config

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def generate_gpt_response(user_name, birth_date, category):
    prompt = (
        f"У вас есть пользователь с именем {user_name}, дата рождения {birth_date}. "
        f"Пользователь выбрал категорию '{category}'. Составь матрицу судьбы для этой категории, "
        f"учитывая информацию о пользователе и его выбор. Ответ должен быть информативным и подходящим "
        f"для выбранной категории."
    )

    messages = [{"role": "user", "content": prompt}]

    response = await client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo"
    )

    return response.choices[0].message.content
