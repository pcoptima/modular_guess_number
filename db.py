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


if __name__ == '__main__':
    init_db()
