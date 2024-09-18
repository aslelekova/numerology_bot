
import sqlite3


async def get_subscription_details(user_id: int):
    conn = sqlite3.connect('users.db') 
    cursor = conn.cursor()
    
    cursor.execute("SELECT subscription_active, readings_left, questions_left FROM login_id WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
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
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT questions_left FROM login_id WHERE id = ?", (user_id,))
    data = cursor.fetchone()
    connection.close()
    return data[0] if data else 0

async def update_user_readings_left(user_id: int, new_readings_left: int):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE login_id SET readings_left = ? WHERE id = ?",
        (new_readings_left, user_id)
    )
    conn.commit()
    conn.close()

async def update_subscription_status(user_id: int, status: str):
    connection = sqlite3.connect("your_database.db")
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE login_id SET subscription_status = ? WHERE id = ?",
        (status, user_id)
    )
    connection.commit()
    connection.close()

async def update_questions_left(user_id: int, questions_left: int):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE login_id SET questions_left = ? WHERE id = ?", (questions_left, user_id))
    connection.commit()
    connection.close()