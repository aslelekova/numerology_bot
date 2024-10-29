import aiosqlite
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiosqlite import cursor

from keyboards.main_menu_keyboard import main_menu_keyboard
from services.db_service import user_exists, add_user, get_questions_left, update_questions_left
from services.message_service import save_message_id

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    start_command = message.text

    if not await user_exists(user_id):
        referrer_id = str(start_command[7:])

        if referrer_id:
            if referrer_id != str(user_id):
                await add_user(user_id, referrer_id)

                data = await state.get_data()
                link_message_id = data.get("link_message_id")

                if link_message_id:
                    try:
                        await message.bot.delete_message(chat_id=message.chat.id, message_id=link_message_id)
                    except Exception as e:
                        print(f"Ошибка при удалении сообщения: {e}")

                try:
                    question = await message.bot.send_message(referrer_id,
                        f"По вашей ссылке зарегистрировался новый пользователь! Вы можете задать бесплатный вопрос!",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_free_question")]
                        ]),
                        parse_mode="HTML"
                    )
                    print(question.message_id)
                    await state.update_data(question_id=question.message_id)
                    await save_message_id(state, question.message_id)

                    questions_left = await get_questions_left(int(referrer_id))
                    await update_questions_left(int(referrer_id), questions_left + 1)
                except Exception as e:


                    print(f"Ошибка при отправке сообщения рефереру: {e}")
            else:
                await message.answer("Нельзя регистрироваться по собственной реферальной ссылке!")
        else:
            await add_user(user_id)

    user_data = await state.get_data()
    user_name = user_data.get("user_name") or message.from_user.first_name


    await message.answer(
        f"Добрый день, {user_name}!\n\nМы рады помочь вам с расчетом матрицы судьбы, нумерологии, "
        "совместимости, карьерного успеха, богатства и других вопросов.\n\n<b>После каждого расчета вы "
        "сможете задать любой вопрос.</b> С чего начнем?",
        reply_markup=main_menu_keyboard()
    )

    await state.clear()


@router.message(Command("users_info"))
async def users_info_command(message: types.Message, state: FSMContext):
    if message.from_user.id == 524763432 or message.from_user.id == 501957101 or message.from_user.id == 965257572:
        async with aiosqlite.connect('/app/users.db') as db:
            async with db.execute("SELECT COUNT(*) FROM login_id") as cursor:
                total_users = await cursor.fetchone()

            async with db.execute("SELECT COUNT(*) FROM login_id WHERE subscription_active = 1") as cursor:
                active_subscriptions = await cursor.fetchone()

            async with db.execute("SELECT COUNT(*) FROM login_id WHERE tariff = 'Тариф 1'") as cursor:
                tariff_1_users = await cursor.fetchone()

            async with db.execute("SELECT COUNT(*) FROM login_id WHERE tariff = 'Тариф 2'") as cursor:
                tariff_2_users = await cursor.fetchone()

            async with db.execute("SELECT COUNT(*) FROM login_id WHERE tariff = 'Тариф 3'") as cursor:
                tariff_3_users = await cursor.fetchone()

            async with db.execute("SELECT COUNT(*) FROM login_id WHERE referred_id IS NOT NULL") as cursor:
                referred_users = await cursor.fetchone()

        total_users_count = total_users[0] if total_users else 0
        active_subscriptions_count = active_subscriptions[0] if active_subscriptions else 0
        tariff_1_users_count = tariff_1_users[0] if tariff_1_users else 0
        tariff_2_users_count = tariff_2_users[0] if tariff_2_users else 0
        tariff_3_users_count = tariff_3_users[0] if tariff_3_users else 0
        referred_users_count = referred_users[0] if referred_users else 0

        await message.answer(
            f"Общее количество пользователей: {total_users_count}\n"
            f"Количество активных подписок: {active_subscriptions_count}\n"
            f"Количество пользователей с Тариф 1: {tariff_1_users_count}\n"
            f"Количество пользователей с Тариф 2: {tariff_2_users_count}\n"
            f"Количество пользователей с Тариф 3: {tariff_3_users_count}\n"
            f"Количество приглашенных пользователей: {referred_users_count}"
        )
    else:
        mes_access = await message.answer("У вас нет доступа к этой команде.")
        await save_message_id(state, mes_access.message_id)


@router.message(Command('broadcast'))
async def broadcast_message(message: types.Message):
    # Проверка, что команда отправлена администратором (добавьте ваш user_id)
    admin_id = 524763432  # Замените на свой ID
    if message.from_user.id != admin_id:
        return

    # Сообщение для рассылки
    broadcast_text = "<b>🔮 Сделай свой нумерологический расклад по лучшей цене — всего за 290 рублей! Горящее предложение ❤️‍</b>🔥"
    target_user_id = 7919534966
    async with aiosqlite.connect('/app/users.db') as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            users = await cursor.fetchall()  # Получаем всех пользователей

    if (target_user_id,) in users:
        try:
            await message.bot.send_message(target_user_id, broadcast_text)
            print(f"Сообщение отправлено пользователю {target_user_id}")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {target_user_id}: {e}")
    else:
        print(f"Пользователь с ID {target_user_id} не найден в базе данных.")