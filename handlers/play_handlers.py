from aiogram import types
from aiogram.fsm.context import FSMContext
from typing import Dict, Any, List
from random import randint
from lexicon import LEXICON
from states import GameStates
from keyboards import game_menu_keyboard, settings_menu_keyboard
from db import save_game_data, save_user_state, increment_games_lost, get_max_game_id, set_attempts_left
import asyncio  # Добавлено для работы с таймером


async def check_missing_settings(data: Dict[str, Any]) -> List[str]:
    """
    Проверяет, какие настройки отсутствуют в данных состояния.
    Возвращает список отсутствующих настроек.
    """
    missing_settings = []
    if 'range_start' not in data or 'range_end' not in data:
        missing_settings.append("Диапазон чисел")
    if 'time_limit' not in data:
        missing_settings.append("Время")
    if 'attempts' not in data:
        missing_settings.append("Попыток")
    return missing_settings


async def start_game_timer(state: FSMContext, user_id: int, data: Dict[str, Any], callback_query: types.CallbackQuery) -> None:
    """
    Запускает таймер игры. Если время истекает, завершает игру,
    обновляет состояние пользователя и сохраняет результат как проигрыш.
    """
    async def game_timer():
        await asyncio.sleep(data['time_limit'])
        current_state = await state.get_state()
        if current_state == GameStates.game:
            game_id = await get_max_game_id(user_id)
            await save_game_data(game_id=game_id, user_id=user_id, results="lost")
            await state.set_state(GameStates.out_game)
            await save_user_state(user_id, "out_game")
            await increment_games_lost(user_id)
            await callback_query.message.answer(
                LEXICON["game_lost_time"].format(
                    time_limit=data['time_limit'])
            )
    asyncio.create_task(game_timer())


async def initialize_game(callback_query: types.CallbackQuery, state: FSMContext, data: Dict[str, Any]) -> None:
    """
    Инициализирует игру: устанавливает состояние, сохраняет целевое число,
    запускает таймер и отправляет сообщение с приглашением к игре.
    """
    user_id = callback_query.from_user.id
    await state.set_state(GameStates.game)
    await save_user_state(user_id, "game")
    target_number = randint(data['range_start'], data['range_end'])
    if user_id is None:
        print("Ошибка: не удалось определить ID пользователя.")
        return
    await state.update_data(target_number=target_number)
    await save_game_data(user_id=user_id, target_number=target_number)
    await start_game_timer(state, user_id, data, callback_query)
    attempts_left = await set_attempts_left(user_id)
    await callback_query.message.answer(
        LEXICON["play_prompt"].format(
            attempts_left=attempts_left
        ),
        reply_markup=game_menu_keyboard()
    )
    await callback_query.answer()


async def process_play(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Основной метод для обработки команды начала игры.
    Проверяет настройки и запускает игру, если все настройки указаны.
    """
    data = await state.get_data()
    missing_settings = await check_missing_settings(data)
    if missing_settings:
        await callback_query.message.answer(
            LEXICON["missing_settings"].format(
                missing_settings=", ".join(missing_settings)),
            reply_markup=settings_menu_keyboard()
        )
        await callback_query.answer()
    else:
        await initialize_game(callback_query, state, data)
