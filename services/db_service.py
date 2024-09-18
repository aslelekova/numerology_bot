
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