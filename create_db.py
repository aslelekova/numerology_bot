import aiosqlite
import asyncio

async def create_db():
    async with aiosqlite.connect('/app/users.db') as db:
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

if __name__ == "__main__":
    asyncio.run(create_db())
