import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'database.sqlite')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            phone_number TEXT PRIMARY KEY,
            state TEXT DEFAULT 'START',
            data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

class SessionManager:
    @staticmethod
    def get_session(phone_number):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT state, data FROM sessions WHERE phone_number = ?', (phone_number,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {'state': row[0], 'data': json.loads(row[1])}
        return {'state': 'START', 'data': {}}

    @staticmethod
    def update_session(phone_number, state, data):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        data_json = json.dumps(data)
        cursor.execute('''
            INSERT INTO sessions (phone_number, state, data, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(phone_number) DO UPDATE SET
                state = excluded.state,
                data = excluded.data,
                updated_at = CURRENT_TIMESTAMP
        ''', (phone_number, state, data_json))
        conn.commit()
        conn.close()

    @staticmethod
    def clear_session(phone_number):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE phone_number = ?', (phone_number,))
        conn.commit()
        conn.close()
