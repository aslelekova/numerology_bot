import sqlite3

def initialize_database():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_id (
            id INTEGER PRIMARY KEY,
            tariff TEXT DEFAULT 'none',
            readings_left INTEGER DEFAULT 0,
            questions_left INTEGER DEFAULT 0
        )
    """)
    connect.commit()
    connect.close()
