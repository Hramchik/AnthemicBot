import sqlite3

def createDB():
    conn = sqlite3.connect('database/request.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL,
        nickname TEXT NOT NULL,
        status TEXT NOT NULL
        )
        ''')
    conn.commit()
    conn.close()
createDB()