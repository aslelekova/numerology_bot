import aiosqlite


async def get_subscription_details(user_id: int):
    async with aiosqlite.connect('users.db') as conn:
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
    async with aiosqlite.connect('users.db') as connection:
        cursor = await connection.execute(
            "SELECT questions_left FROM login_id WHERE id = ?",
            (user_id,)
        )
        data = await cursor.fetchone()
    return data[0] if data else 0

async def update_user_readings_left(user_id: int, new_readings_left: int):
    async with aiosqlite.connect('users.db') as conn:
        await conn.execute(
            "UPDATE login_id SET readings_left = ? WHERE id = ?",
            (new_readings_left, user_id)
        )
        await conn.commit()

async def update_subscription_status(user_id: int, status: str):
    async with aiosqlite.connect("users.db") as connection:
        await connection.execute(
            "UPDATE login_id SET subscription_active = ? WHERE id = ?",
            (status, user_id)
        )
        await connection.commit()

async def update_questions_left(user_id: int, questions_left: int):
    async with aiosqlite.connect('users.db') as connection:
        await connection.execute(
            "UPDATE login_id SET questions_left = ? WHERE id = ?",
            (questions_left, user_id)
        )
        await connection.commit()



async def save_share_link(user_id: int, unique_id: str):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            "INSERT INTO share_links (user_id, unique_id) VALUES (?, ?)",
            (user_id, unique_id)
        )
        await db.commit()


async def get_user_by_share_link(unique_id: str) -> int:
    async with aiosqlite.connect('database.db') as db:
        async with db.execute("SELECT user_id FROM share_links WHERE unique_id = ?", (unique_id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                return result[0]
            return None


async def increment_user_questions(user_id: int, count: int):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            "UPDATE users SET questions_left = questions_left + ? WHERE user_id = ?",
            (count, user_id)
        )
        await db.commit()
