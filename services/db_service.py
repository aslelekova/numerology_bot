import os

import aiosqlite

from main import logger


async def get_subscription_details(user_id: int):
    async with aiosqlite.connect('/app/users.db') as conn:
        cursor = await conn.execute(
            "SELECT subscription_active, readings_left, questions_left FROM login_id WHERE id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()

    if result:
        return {
            "subscription_active": bool(result[0]),
            "readings_left": result[1],
            "questions_left": result[2]
        }
    return {
        "subscription_active": False,
        "readings_left": 0,
        "questions_left": 0
    }


async def get_questions_left(user_id: int) -> int:
    async with aiosqlite.connect('/app/users.db') as connection:
        cursor = await connection.execute(
            "SELECT questions_left FROM login_id WHERE id = ?",
            (user_id,)
        )
        data = await cursor.fetchone()
    return data[0] if data else 0


async def update_user_readings_left(user_id: int, new_readings_left: int):
    async with aiosqlite.connect('/app/users.db') as conn:
        await conn.execute(
            "UPDATE login_id SET readings_left = ? WHERE id = ?",
            (new_readings_left, user_id)
        )
        await conn.commit()


async def update_subscription_status(user_id: int, status: str):
    async with aiosqlite.connect("/app/users.db") as connection:
        await connection.execute(
            "UPDATE login_id SET subscription_active = ? WHERE id = ?",
            (status, user_id)
        )
        await connection.commit()


async def update_questions_left(user_id: int, questions_left: int):
    async with aiosqlite.connect('/app/users.db') as connection:
        await connection.execute(
            "UPDATE login_id SET questions_left = ? WHERE id = ?",
            (questions_left, user_id)
        )
        await connection.commit()

async def setup_db():
    db_directory = '/app'
    db_path = os.path.join(db_directory, 'users.db')

    # Проверка существования директории и создание её при отсутствии
    if not os.path.exists(db_directory):
        os.makedirs(db_directory)

    if not os.path.exists(db_path):
        logger.info("Создаётся новая база данных...")
    else:
        logger.info("База данных уже существует.")

    try:
        async with aiosqlite.connect(db_path) as db:
            logger.info("Успешное подключение к базе данных.")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS login_id (
                    id INTEGER PRIMARY KEY,
                    tariff TEXT DEFAULT 'none',
                    readings_left INTEGER DEFAULT 0,
                    questions_left INTEGER DEFAULT 1, 
                    subscription_active BOOLEAN DEFAULT 0,
                    referred_id INTEGER DEFAULT NULL
                )
            """)
            await db.commit()
            logger.info("Таблица успешно создана или уже существует.")
    except Exception as e:
        logger.exception("Ошибка при подключении к базе данных: %s", e)

async def user_exists(user_id):
    async with aiosqlite.connect('/app/users.db') as db:
        cursor = await db.execute("SELECT id FROM login_id WHERE id = ?", (user_id,))
        data = await cursor.fetchone()
        return data is not None

async def add_user(user_id, referred_id=None):
    async with aiosqlite.connect('/app/users.db') as db:
        await db.execute("INSERT INTO login_id (id, referred_id) VALUES (?, ?)", (user_id, referred_id))
        await db.commit()
