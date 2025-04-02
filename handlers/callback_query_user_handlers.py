from aiogram import types
from aiogram.fsm.context import FSMContext
from lexicon import LEXICON
from states import GameStates
from keyboards import (my_settings_menu_keyboard, settings_menu_keyboard,
                       main_menu_keyboard, game_setting_keyboard)
from db import save_user_state, reset_settings, load_user_settings, count_and_update_unfinished_games


async def process_rules(callback_query: types.CallbackQuery) -> None:
    """
    Обрабатывает запрос на отображение правил игры.
    """
    await callback_query.message.answer(LEXICON["rules"], reply_markup=game_setting_keyboard())
    await callback_query.answer()


async def get_stats(callback_query: types.CallbackQuery) -> None:
    """
    Отправляет статистику пользователя: количество побед, поражений и незавершенных игр.
    """
    user_id = callback_query.from_user.id
    await count_and_update_unfinished_games(user_id)
    all_data_user = await load_user_settings(user_id)
    games_won = all_data_user[5]
    games_lost = all_data_user[6]
    not_finished = all_data_user[7]
    await callback_query.message.answer(LEXICON["statistics"].format(
        games_won=games_won,
        games_lost=games_lost,
        not_finished=not_finished
    ), reply_markup=main_menu_keyboard())
    await callback_query.answer()


async def process_settings(callback_query: types.CallbackQuery) -> None:
    """
    Отправляет сообщение с настройками игры.
    """
    await callback_query.message.answer(LEXICON["settings"], reply_markup=settings_menu_keyboard())
    await callback_query.answer()


async def process_interrupt(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Сбрасывает настройки пользователя и переводит игру в состояние 'вне игры'.
    """
    user_id = callback_query.from_user.id
    await state.clear()
    await reset_settings(user_id)
    await state.set_state(GameStates.out_game)
    await save_user_state(user_id, "out_game")
    await callback_query.message.answer(LEXICON["interrupt"], reply_markup=my_settings_menu_keyboard())
    await callback_query.answer()


async def process_my_settings(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Отправляет текущие настройки пользователя.
    """
    user_id = callback_query.from_user.id
    settings = await load_user_settings(user_id)
    if settings:
        range_start, range_end, time_limit, attempts, _, _, _, _ = settings
        await state.update_data(
            range_start=range_start,
            range_end=range_end,
            time_limit=time_limit,
            attempts=attempts
        )
        await callback_query.message.answer(LEXICON["my_settings"].format(
            range_start=range_start,
            range_end=range_end,
            time_limit=time_limit,
            attempts=attempts
        ), reply_markup=my_settings_menu_keyboard())
    else:
        await callback_query.message.answer(LEXICON["my_settings_error"], reply_markup=my_settings_menu_keyboard())
    await callback_query.answer()


async def process_set_range(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Переводит игру в состояние установки диапазона чисел.
    """
    await state.set_state(GameStates.set_range)
    await callback_query.message.answer(LEXICON["set_range_prompt"], reply_markup=settings_menu_keyboard())
    await callback_query.answer()


async def process_set_time(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Переводит игру в состояние установки лимита времени.
    """
    await state.set_state(GameStates.set_time)
    await callback_query.message.answer(LEXICON["set_time_prompt"], reply_markup=settings_menu_keyboard())
    await callback_query.answer()


async def process_set_attempts(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Переводит игру в состояние установки количества попыток.
    """
    await state.set_state(GameStates.set_attempts)
    await callback_query.message.answer(LEXICON["set_attempts_prompt"], reply_markup=settings_menu_keyboard())
    await callback_query.answer()
