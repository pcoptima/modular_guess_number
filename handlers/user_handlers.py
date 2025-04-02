from aiogram import types, F
from aiogram.fsm.context import FSMContext
from lexicon import LEXICON
from states import GameStates
from keyboards import (start_menu_keyboard, my_settings_menu_keyboard,
                       settings_menu_keyboard, main_menu_keyboard, game_setting_keyboard)
from db import save_user_settings, load_user_settings, save_user_state, reset_settings, count_and_update_unfinished_games


# async def load_settings_from_db(user_id: int, state: FSMContext) -> tuple:
#     """
#     Загружает настройки пользователя из базы данных и обновляет состояние FSM.
#     Возвращает настройки: диапазон чисел, лимит времени, количество попыток.
#     """
#     settings = await load_user_settings(user_id)
#     if settings:
#         range_start, range_end, time_limit, attempts, _, _, _, _ = settings
#         await state.update_data(
#             range_start=range_start,
#             range_end=range_end,
#             time_limit=time_limit,
#             attempts=attempts
#         )
#         return range_start, range_end, time_limit, attempts
#     return "не указано", "не указано", "не указано", "не указано"
