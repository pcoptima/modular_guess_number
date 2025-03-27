from aiogram import types, F
from aiogram.fsm.context import FSMContext
from lexicon import LEXICON
from states import GameStates
from keyboards import (start_menu_keyboard, my_settings_menu_keyboard,
                       settings_menu_keyboard, main_menu_keyboard, game_menu_keyboard)


async def send_welcome(message: types.Message):
    await message.answer(LEXICON["welcome"], reply_markup=start_menu_keyboard())


async def process_help(message: types.Message):
    await message.answer(LEXICON["rules"])


async def process_rules(callback_query: types.CallbackQuery):
    await callback_query.message.answer(LEXICON["rules"], reply_markup=main_menu_keyboard())
    await callback_query.answer()


async def process_settings(callback_query: types.CallbackQuery):
    await callback_query.message.answer(LEXICON["settings"], reply_markup=settings_menu_keyboard())
    await callback_query.answer()


async def process_my_settings(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    range_start = data.get('range_start')
    range_end = data.get('range_end')
    time_limit = data.get('time_limit')
    attempts = data.get('attempts')
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
        # Сохраняем данные в состояние
        await state.update_data(range_start=range_start, range_end=range_end)
        # Устанавливаем состояние out_game
        await state.set_state(GameStates.out_game)
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
        # Сохраняем данные в состояние
        await state.update_data(time_limit=time_limit)
        # Устанавливаем состояние set_time
        await state.set_state(GameStates.set_time)
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
        # Сохраняем данные в состояние
        await state.update_data(attempts=attempts)
        # Устанавливаем состояние set_attempts
        await state.set_state(GameStates.set_attempts)
        await message.reply(LEXICON["set_attempts_success"], reply_markup=settings_menu_keyboard())
    except ValueError:
        await message.reply(LEXICON["set_attempts_error"])


async def process_play(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()  # Получаем данные из состояния
    # Проверяем, указаны ли все необходимые настройки
    if 'range_start' not in data or 'range_end' not in data or 'time_limit' not in data or 'attempts' not in data:
        missing_settings = []
        # Если диапазон чисел не указан, добавляем его в список отсутствующих настроек
        if 'range_start' not in data or 'range_end' not in data:
            missing_settings.append("Диапазон чисел")
        # Если лимит времени не указан, добавляем его в список отсутствующих настроек
        if 'time_limit' not in data:
            missing_settings.append("Время")
        # Если количество попыток не указано, добавляем его в список отсутствующих настроек
        if 'attempts' not in data:
            missing_settings.append("Попыток")
        # Отправляем сообщение с перечислением отсутствующих настроек
        await callback_query.message.answer(
            LEXICON["missing_settings"].format(
                missing_settings=", ".join(missing_settings)),
            reply_markup=settings_menu_keyboard()
        )
        await callback_query.answer()
    else:
        # Если все настройки указаны, переводим бота в состояние игры
        await state.set_state(GameStates.game)
        # ... логика начала игры ...
        # Отправляем сообщение с приглашением ввести число
        await callback_query.message.answer(
            LEXICON["play_prompt"],
            reply_markup=game_menu_keyboard()
        )
        await callback_query.answer()
