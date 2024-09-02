from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import StateFilter
from handlers.sections_handler import client
from handlers.start_handler import cmd_start
from states import QuestionState

router = Router()


@router.callback_query(lambda callback: callback.data == "ask_free_question")
async def ask_free_question_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Отлично! Теперь вы можете задать свой вопрос (Например: 💕 Как улучшить мои отношения с партнером?)\n\n"
        "⚡️ У вас есть 1 бесплатный вопрос"
    )
    await state.set_state(QuestionState.waiting_for_question)


@router.message(StateFilter(QuestionState.waiting_for_question))
async def process_question(message: types.Message, state: FSMContext):
    print("Process question handler triggered")

    user_data = await state.get_data()
    print(f"User data: {user_data}")

    if user_data.get("question_asked", False):
        await message.answer(
            "Упс, похоже у вас закончились бесплатные вопросы, откройте полный доступ к приложению.\n\n⚡️ 0 "
            "бесплатных вопросов"
        )
        return

    user_question = message.text
    user_name = user_data.get("user_name", "Пользователь")
    user_date = user_data.get("user_date", "неизвестна")

    prompt = (
        f"У вас есть пользователь с именем {user_name}, дата рождения {user_date}. "
        f"Пользователь задал следующий вопрос по матрице судьбы: '{user_question}'. Напишите ответ, "
        f"учитывая информацию о пользователе и его вопрос."
    )

    messages = [{"role": "user", "content": prompt}]

    generating_message = await message.answer("⏳")

    try:
        response = await client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo"
        )
        response_text = response.choices[0].message.content
    except Exception as e:
        await generating_message.delete()
        await message.answer("Произошла ошибка при генерации ответа. Пожалуйста, попробуйте позже.")
        return

    await generating_message.delete()

    response_message = await message.answer(response_text)

    suggestion_prompt = (
        f"Предложи три вопроса (пронумеруй их так: 🔮 -), разделяй как \\n, на основе следующего вопроса пользователя: '{user_question}'. Вопросы должны быть "
        f"краткими и направленными на разные аспекты жизни."
    )

    suggestions_messages = [{"role": "user", "content": suggestion_prompt}]

    try:
        suggestion_response = await client.chat.completions.create(
            messages=suggestions_messages,
            model="gpt-3.5-turbo"
        )
        suggestions_text = suggestion_response.choices[0].message.content
    except Exception as e:
        suggestions_text = (
            "🔮 - Какое будущее меня ожидает?\n"
            "🔮 - Какие таланты и способности мне развивать?\n"
            "🔮 - Как привлечь финансовое благополучие?"
        )
        print(f"Error generating suggestions: {e}")

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить полный доступ", callback_data="get_full_access")],
            [InlineKeyboardButton(text="Задать еще один вопрос (поделиться с другом)",
                                  callback_data="share_and_ask")],
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
        ]
    )

    suggestion_message = await message.answer(
        f"💫 <b>Задавайте еще больше вопросов своему ассистенту!</b> Вот примеры вопросов, которые могут вас "
        f"заинтересовать:\n\n"
        f"{suggestions_text}\n\n"
        "ПОДЕЛИТЕСЬ с другом и получите возможность задать <b>еще один бесплатный вопрос</b>, или ПОЛУЧИТЕ ПОЛНЫЙ "
        "ДОСТУП к боту,"
        "чтобы задавать неограниченное количество вопросов и делать любые расклады! 😍",
        reply_markup=inline_keyboard
    )

    # Сохраняем ID последних двух сообщений в состояние
    await state.update_data(previous_message_ids=[response_message.message_id, suggestion_message.message_id])
    await state.update_data(question_asked=True)


@router.callback_query(lambda callback: callback.data == "main_menu")
async def main_menu_callback(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        # Получаем ID сообщений из состояния
        user_data = await state.get_data()
        previous_message_ids = user_data.get("previous_message_ids", [])
        first_message_id = user_data.get("first_message_id")
        question_prompt_message_id = user_data.get("question_prompt_message_id")

        # Удаляем предыдущие сообщения по сохраненным ID
        for message_id in previous_message_ids + [first_message_id, question_prompt_message_id]:
            if message_id:
                try:
                    await callback_query.message.bot.delete_message(callback_query.message.chat.id, message_id)
                except Exception as e:
                    if "message to delete not found" not in str(e):
                        print(f"Error deleting message with ID {message_id}: {e}")

        await callback_query.message.delete()

    except Exception as e:
        print(f"Error deleting messages: {e}")

    await cmd_start(callback_query.message)
