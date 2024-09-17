import sqlite3

def get_db_connection():
    conn = sqlite3.connect('users.db')  # Имя базы данных
    conn.row_factory = sqlite3.Row
    return conn

# Создаем таблицу пользователей, если её нет
def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        free_questions INTEGER DEFAULT 0,
        free_spreads INTEGER DEFAULT 0,
        subscription_status BOOLEAN DEFAULT FALSE
    )''')
    conn.commit()
    conn.close()

# Функция для получения пользователя по Telegram ID
def get_user_by_telegram_id(telegram_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Функция для создания нового пользователя
def create_user(telegram_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (telegram_id, free_questions, free_spreads, subscription_status) VALUES (?, ?, ?, ?)",
                   (telegram_id, 5, 3, False))  # по умолчанию 5 вопросов и 3 расклада
    conn.commit()
    conn.close()

# Функция для обновления количества бесплатных вопросов
def update_free_questions(telegram_id, questions_left):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET free_questions = ? WHERE telegram_id = ?", (questions_left, telegram_id))
    conn.commit()
    conn.close()

# Функция для обновления количества бесплатных раскладов
def update_free_spreads(telegram_id, spreads_left):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET free_spreads = ? WHERE telegram_id = ?", (spreads_left, telegram_id))
    conn.commit()
    conn.close()

# Функция для обновления статуса подписки
def update_subscription_status(telegram_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET subscription_status = ? WHERE telegram_id = ?", (status, telegram_id))
    conn.commit()
    conn.close()

# Инициализация базы данных
if __name__ == '__main__':
    create_users_table()
