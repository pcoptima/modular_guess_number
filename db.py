import sqlite3


async def init_db():
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


async def save_user_settings(user_id, range_start=None, range_end=None, time_limit=None, attempts=None, fsm_state=None):
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


async def save_game_data(game_id=None, user_id=None, target_number=None, attempts_left=None, start_time=None):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    try:
        # Проверяем, существует ли пользователь с данным user_id
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            raise ValueError(
                f"User with user_id {user_id} does not exist in the users table.")

        # Если game_id передан, обновляем существующую запись
        if game_id is not None:
            cursor.execute(
                'SELECT user_id, target_number, attempts_left, start_time FROM games WHERE game_id = ?', (game_id,))
            current_game = cursor.fetchone()

            if current_game:
                user_id = user_id if user_id is not None else current_game[0]
                target_number = target_number if target_number is not None else current_game[
                    1]
                attempts_left = attempts_left if attempts_left is not None else current_game[
                    2]
                start_time = start_time if start_time is not None else current_game[3]
                cursor.execute('''
                    UPDATE games
                    SET user_id = ?, target_number = ?, attempts_left = ?, start_time = ?
                    WHERE game_id = ?
                ''', (user_id, target_number, attempts_left, start_time, game_id))
        else:
            # Если game_id не передан, создаем новую запись
            # Устанавливаем значения по умолчанию для attempts_left и start_time
            attempts_left = attempts_left if attempts_left is not None else 0
            start_time = start_time if start_time is not None else None
            cursor.execute('''
                INSERT INTO games (user_id, target_number, attempts_left, start_time)
                VALUES (?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
            ''', (user_id, target_number, attempts_left, start_time))

        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except ValueError as ve:
        print(f"Value error: {ve}")
    finally:
        conn.close()


async def load_user_settings(user_id):
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


async def get_game_id(user_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT game_id
        FROM games
        WHERE user_id = ? AND EXISTS (
            SELECT 1
            FROM users
            WHERE users.user_id = games.user_id AND fsm_state = 'game'
        )
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


if __name__ == '__main__':
    init_db()
