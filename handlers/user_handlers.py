from aiogram import types, F
from aiogram.fsm.context import FSMContext
from lexicon import LEXICON
from states import GameStates
from keyboards import (start_menu_keyboard, my_settings_menu_keyboard,
                       settings_menu_keyboard, main_menu_keyboard, game_setting_keyboard)
from db import save_user_settings, load_user_settings, save_user_state, reset_settings, count_and_update_unfinished_games


async def send_welcome(message: types.Message):
    await message.answer(LEXICON["welcome"], reply_markup=start_menu_keyboard())


async def process_help(message: types.Message):
    await message.answer(LEXICON["rules"], reply_markup=game_setting_keyboard())


async def process_rules(callback_query: types.CallbackQuery):
    await callback_query.message.answer(LEXICON["rules"], reply_markup=game_setting_keyboard())
    await callback_query.answer()


async def get_stats(callback_query: types.CallbackQuery):
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


async def process_settings(callback_query: types.CallbackQuery):
    await callback_query.message.answer(LEXICON["settings"], reply_markup=settings_menu_keyboard())
    await callback_query.answer()


async def load_settings_from_db(user_id: int, state: FSMContext):
    settings = await load_user_settings(user_id)
    if settings:
        range_start, range_end, time_limit, attempts, _, _, _, _ = settings
        await state.update_data(
            range_start=range_start,
            range_end=range_end,
            time_limit=time_limit,
            attempts=attempts
        )
        return range_start, range_end, time_limit, attempts
    return "не указано", "не указано", "не указано", "не указано"


async def process_interrupt(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    # Сбрасываем настройки пользователя
    await state.clear()
    await reset_settings(user_id)
    # Устанавливаем состояние игры
    await state.set_state(GameStates.out_game)
    await save_user_state(user_id, "out_game")  # Обновляем состояние в БД
    await callback_query.message.answer(LEXICON["interrupt"], reply_markup=my_settings_menu_keyboard())
    await callback_query.answer()


async def process_my_settings(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    range_start, range_end, time_limit, attempts = await load_settings_from_db(user_id, state)
    await callback_query.message.answer(LEXICON["my_settings"].format(
        range_start=range_start,
        range_end=range_end,
        time_limit=time_limit,
        attempts=attempts
    ), reply_markup=my_settings_menu_keyboard())
    await callback_query.answer()


async def process_set_range(callback_query: types.CallbackQuery, state: FSMContext):
    # Устанавливаем состояние set_range
    await state.set_state(GameStates.set_range)
    await callback_query.message.answer(LEXICON["set_range_prompt"], reply_markup=settings_menu_keyboard())
    await callback_query.answer()


async def set_range(message: types.Message, state: FSMContext):
    try:
        range_start, range_end = map(int, message.text.split())
        user_id = message.from_user.id
        # Сохраняем данные в состояние и базу данных
        await state.update_data(range_start=range_start, range_end=range_end)
        await save_user_settings(user_id, range_start=range_start,
                                 range_end=range_end)
        await state.set_state(GameStates.out_game)
        await save_user_state(user_id, "out_game")  # Обновляем состояние в БД
        await message.reply(LEXICON["set_range_success"], reply_markup=settings_menu_keyboard())
    except ValueError:
        await message.reply(LEXICON["set_range_error"])


async def process_set_time(callback_query: types.CallbackQuery, state: FSMContext):
    # Устанавливаем состояние set_time
    await state.set_state(GameStates.set_time)
    await callback_query.message.answer(LEXICON["set_time_prompt"], reply_markup=settings_menu_keyboard())
    await callback_query.answer()


async def set_time(message: types.Message, state: FSMContext):
    try:
        time_limit = int(message.text)
        user_id = message.from_user.id
        # Сохраняем данные в состояние и базу данных
        await state.update_data(time_limit=time_limit)
        await save_user_settings(user_id, time_limit=time_limit)
        await state.set_state(GameStates.out_game)
        await save_user_state(user_id, "out_game")  # Обновляем состояние в БД
        await message.reply(LEXICON["set_time_success"], reply_markup=settings_menu_keyboard())
    except ValueError:
        await message.reply(LEXICON["set_time_error"])


async def process_set_attempts(callback_query: types.CallbackQuery, state: FSMContext):
    # Устанавливаем состояние set_attempts
    await state.set_state(GameStates.set_attempts)
    await callback_query.message.answer(LEXICON["set_attempts_prompt"], reply_markup=settings_menu_keyboard())
    await callback_query.answer()


async def set_attempts(message: types.Message, state: FSMContext):
    try:
        attempts = int(message.text)
        user_id = message.from_user.id
        # Сохраняем данные в состояние и базу данных
        await state.update_data(attempts=attempts)
        await save_user_settings(user_id, attempts=attempts)
        await state.set_state(GameStates.out_game)
        await save_user_state(user_id, "out_game")  # Обновляем состояние в БД
        await message.reply(LEXICON["set_attempts_success"], reply_markup=settings_menu_keyboard())
    except ValueError:
        await message.reply(LEXICON["set_attempts_error"])


async def handle_out_of_game_message(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await message.answer(LEXICON["out_game"],
                             reply_markup=main_menu_keyboard()
                             )
    else:
        await message.answer(LEXICON["only_numbers"], reply_markup=main_menu_keyboard())
