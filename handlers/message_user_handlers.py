import html
from aiogram import types
from aiogram.fsm.context import FSMContext
from lexicon import LEXICON
from states import GameStates
from db import save_user_settings, save_user_state
from keyboards import settings_menu_keyboard, main_menu_keyboard, start_menu_keyboard


async def send_welcome(message: types.Message) -> None:
    """
    Отправляет приветственное сообщение пользователю.
    """
    user = html.escape(message.from_user.full_name)
    await message.answer(LEXICON["welcome"].format(
        user=user
    ), reply_markup=start_menu_keyboard())


async def process_help(message: types.Message) -> None:
    """
    Отправляет сообщение с правилами игры.
    """
    await message.answer(LEXICON["rules"], reply_markup=settings_menu_keyboard())


async def set_range(message: types.Message, state: FSMContext) -> None:
    """
    Устанавливает диапазон чисел для игры.
    """
    try:
        range_start, range_end = map(int, message.text.split())
        user_id = message.from_user.id
        await state.update_data(range_start=range_start, range_end=range_end)
        await save_user_settings(user_id, range_start=range_start, range_end=range_end)
        await state.set_state(GameStates.out_game)
        await save_user_state(user_id, "out_game")
        await message.reply(LEXICON["set_range_success"], reply_markup=settings_menu_keyboard())
    except ValueError:
        await message.reply(LEXICON["set_range_error"])


async def set_time(message: types.Message, state: FSMContext) -> None:
    """
    Устанавливает лимит времени для игры.
    """
    try:
        time_limit = int(message.text)
        user_id = message.from_user.id
        await state.update_data(time_limit=time_limit)
        await save_user_settings(user_id, time_limit=time_limit)
        await state.set_state(GameStates.out_game)
        await save_user_state(user_id, "out_game")
        await message.reply(LEXICON["set_time_success"], reply_markup=settings_menu_keyboard())
    except ValueError:
        await message.reply(LEXICON["set_time_error"])


async def set_attempts(message: types.Message, state: FSMContext) -> None:
    """
    Устанавливает количество попыток для игры.
    """
    try:
        attempts = int(message.text)
        user_id = message.from_user.id
        await state.update_data(attempts=attempts)
        await save_user_settings(user_id, attempts=attempts)
        await state.set_state(GameStates.out_game)
        await save_user_state(user_id, "out_game")
        await message.reply(LEXICON["set_attempts_success"], reply_markup=settings_menu_keyboard())
    except ValueError:
        await message.reply(LEXICON["set_attempts_error"])


async def handle_out_of_game_message(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает сообщения, отправленные пользователем, когда игра находится в состоянии 'вне игры'.
    """
    if message.text.isdigit():
        await message.answer(LEXICON["out_game"], reply_markup=main_menu_keyboard())
    else:
        await message.answer(LEXICON["only_numbers"], reply_markup=main_menu_keyboard())
