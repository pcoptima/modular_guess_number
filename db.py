import sqlite3


def init_db():
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            range_start INTEGER,
            range_end INTEGER,
            time_limit INTEGER,
            attempts INTEGER,
            games_won INTEGER,
            games_lost INTEGER,
            games_unfinished INTEGER,
            fsm_state TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            target_number INTEGER,
            attempts_left INTEGER,
            start_time TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()


def save_user_settings(user_id, range_start=None, range_end=None, time_limit=None, attempts=None, fsm_state=None):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    # Получаем текущие значения из базы данных
    cursor.execute(
        'SELECT range_start, range_end, time_limit, attempts, fsm_state FROM users WHERE user_id = ?', (user_id,))
    current_settings = cursor.fetchone()

    # Если пользователь уже существует, обновляем только переданные значения
    if current_settings:
        range_start = range_start if range_start is not None else current_settings[0]
        range_end = range_end if range_end is not None else current_settings[1]
        time_limit = time_limit if time_limit is not None else current_settings[2]
        attempts = attempts if attempts is not None else current_settings[3]
        fsm_state = fsm_state if fsm_state is not None else current_settings[4]
        cursor.execute('''
            UPDATE users
            SET range_start = ?, range_end = ?, time_limit = ?, attempts = ?, fsm_state = ?
            WHERE user_id = ?
        ''', (range_start, range_end, time_limit, attempts, fsm_state, user_id))
    else:
        # Если пользователь не существует, создаем новую запись
        cursor.execute('''
            INSERT INTO users (user_id, range_start, range_end, time_limit, attempts, fsm_state)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, range_start, range_end, time_limit, attempts, fsm_state))

    conn.commit()
    conn.close()


def load_user_settings(user_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT range_start, range_end, time_limit, attempts, fsm_state
        FROM users
        WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


if __name__ == '__main__':
    init_db()
