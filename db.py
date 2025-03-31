from typing import Optional, Union
from databases import Database
import aiosqlite


async def init_db() -> None:
    """
    Инициализирует базу данных, создавая таблицы users и games, если они не существуют.
    """
    async with aiosqlite.connect('game.db') as conn:
        await conn.execute('''
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
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                target_number INTEGER,
                attempts_left INTEGER,
                start_time TIMESTAMP,
                results TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        await conn.commit()


async def save_user_settings(
    user_id: int,
    range_start: Optional[int] = None,
    range_end: Optional[int] = None,
    time_limit: Optional[int] = None,
    attempts: Optional[int] = None,
    fsm_state: Optional[str] = None
) -> None:
    """
    Сохраняет или обновляет настройки пользователя в таблице users.
    """
    async with aiosqlite.connect('game.db') as conn:
        cursor = await conn.execute(
            'SELECT range_start, range_end, time_limit, attempts, fsm_state FROM users WHERE user_id = ?', (user_id,))
        current_settings = await cursor.fetchone()

        if current_settings:
            range_start = range_start if range_start is not None else current_settings[0]
            range_end = range_end if range_end is not None else current_settings[1]
            time_limit = time_limit if time_limit is not None else current_settings[2]
            attempts = attempts if attempts is not None else current_settings[3]
            fsm_state = fsm_state if fsm_state is not None else current_settings[4]
            await conn.execute('''
                UPDATE users
                SET range_start = ?, range_end = ?, time_limit = ?, attempts = ?, fsm_state = ?
                WHERE user_id = ?
            ''', (range_start, range_end, time_limit, attempts, fsm_state, user_id))
        else:
            await conn.execute('''
                INSERT INTO users (user_id, range_start, range_end, time_limit, attempts, fsm_state)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, range_start, range_end, time_limit, attempts, fsm_state))

        await conn.commit()


# async def reset_settings(user_id: int) -> None:
#     """
#     Сбрасывает настройки пользователя в таблице users:
#     range_start, range_end, time_limit, attempts устанавливаются в NULL,
#     а fsm_state устанавливается в 'out_game'.
#     """
#     async with aiosqlite.connect('game.db') as conn:
#         await conn.execute('''
#             UPDATE users
#             SET range_start = NULL, range_end = NULL, time_limit = NULL, attempts = NULL, fsm_state = 'out_game'
#             WHERE user_id = ?
#         ''', (user_id,))
#         await conn.commit()


async def save_game_data(
    game_id: Optional[int] = None,
    user_id: Optional[int] = None,
    target_number: Optional[int] = None,
    attempts_left: Optional[int] = None,
    start_time: Optional[Union[str, None]] = None,
    results: Optional[str] = None
) -> None:
    """
    Сохраняет или обновляет данные игры в таблице games.
    """
    async with aiosqlite.connect('game.db') as conn:
        try:
            cursor = await conn.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
            if not await cursor.fetchone():
                raise ValueError(
                    f"User with user_id {user_id} does not exist in the users table.")

            if game_id is not None:
                cursor = await conn.execute(
                    'SELECT user_id, target_number, attempts_left, start_time, results FROM games WHERE game_id = ?', (game_id,))
                current_game = await cursor.fetchone()

                if current_game:
                    user_id = user_id if user_id is not None else current_game[0]
                    target_number = target_number if target_number is not None else current_game[
                        1]
                    attempts_left = attempts_left if attempts_left is not None else current_game[
                        2]
                    start_time = start_time if start_time is not None else current_game[3]
                    results = results if results is not None else current_game[4]
                    await conn.execute('''
                        UPDATE games
                        SET user_id = ?, target_number = ?, attempts_left = ?, start_time = ?, results = ?
                        WHERE game_id = ?
                    ''', (user_id, target_number, attempts_left, start_time, results, game_id))
            else:
                attempts_left = attempts_left if attempts_left is not None else 0
                start_time = start_time if start_time is not None else None
                await conn.execute('''
                    INSERT INTO games (user_id, target_number, attempts_left, start_time, results)
                    VALUES (?, ?, ?, COALESCE(?, DATETIME('now', 'localtime')), ?)
                ''', (user_id, target_number, attempts_left, start_time, results))

            await conn.commit()
        except aiosqlite.Error as e:
            print(f"SQLite error: {e}")
        except ValueError as ve:
            print(f"Value error: {ve}")


async def load_user_settings(user_id: int) -> Optional[tuple]:
    """
    Загружает настройки пользователя из таблицы users по user_id.
    """
    async with aiosqlite.connect('game.db') as conn:
        cursor = await conn.execute('''
            SELECT range_start, range_end, time_limit, attempts, fsm_state
            FROM users
            WHERE user_id = ?
        ''', (user_id,))
        result = await cursor.fetchone()
        return result


async def user_settings_to_dict(user_id: int) -> Optional[dict]:
    """
    Преобразует настройки пользователя из кортежа в словарь с ключами:
    range_start, range_end, time_limit, attempts, fsm_state.
    """
    settings = await load_user_settings(user_id)
    if settings:
        keys = ['range_start', 'range_end',
                'time_limit', 'attempts', 'fsm_state']
        return dict(zip(keys, settings))
    return None


async def get_max_game_id(user_id: int) -> Optional[int]:
    """
    Возвращает максимальный game_id для указанного user_id из таблицы games.
    """
    async with aiosqlite.connect('game.db') as conn:
        cursor = await conn.execute('''
            SELECT MAX(game_id)
            FROM games
            WHERE user_id = ?
        ''', (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else None


async def save_user_state(user_id: int, state: str) -> None:
    """
    Обновляет состояние пользователя (fsm_state) в таблице users.
    """
    async with aiosqlite.connect('game.db') as conn:
        await conn.execute('''
            UPDATE users
            SET fsm_state = ?
            WHERE user_id = ?
        ''', (state, user_id))
        await conn.commit()


async def increment_games_lost(user_id: int) -> None:
    """
    Увеличивает на 1 значение поля games_lost для указанного user_id в таблице users.
    """
    async with aiosqlite.connect('game.db') as conn:
        await conn.execute('''
            UPDATE users
            SET games_lost = games_lost + 1
            WHERE user_id = ?
        ''', (user_id,))
        await conn.commit()


async def set_attempts_left(user_id: int) -> Optional[int]:
    """
    Устанавливает значение attempts_left в таблице games равным attempts из таблицы users,
    если fsm_state равно 'game'.
    """
    async with aiosqlite.connect('game.db') as conn:
        cursor = await conn.execute('''
            SELECT attempts, fsm_state
            FROM users
            WHERE user_id = ?
        ''', (user_id,))
        user = await cursor.fetchone()

        if user and user[1] == 'game':
            # Используем метод get_max_game_id для получения максимального game_id
            max_game_id = await get_max_game_id(user_id)
            if max_game_id:
                await conn.execute('''
                    UPDATE games
                    SET attempts_left = ?
                    WHERE game_id = ?
                ''', (user[0], max_game_id))
                await conn.commit()
                cursor = await conn.execute('''
                    SELECT attempts_left
                    FROM games
                    WHERE game_id = ?
                ''', (max_game_id,))
                result = await cursor.fetchone()
                return result[0] if result else None
