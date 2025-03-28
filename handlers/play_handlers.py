from aiogram import types
from aiogram.fsm.context import FSMContext
from random import randint
from lexicon import LEXICON
from states import GameStates
from keyboards import game_menu_keyboard, settings_menu_keyboard
from db import save_game_data, save_user_state


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
        user_id = callback_query.from_user.id
        # Если все настройки указаны, переводим бота в состояние игры
        await state.set_state(GameStates.game)
        await save_user_state(user_id, "game")
        # ... логика начала игры ...

        # Устанавливаем целевое число и сохраняем его в базу данных
        target_number = randint(data['range_start'], data['range_end'])
        # Проверяем, что user_id не равен None
        if user_id is None:
            print("Ошибка: не удалось определить ID пользователя.")
            return

        await state.update_data(target_number=target_number)
        await save_game_data(user_id=user_id, target_number=target_number)

        # Отправляем сообщение с приглашением ввести число
        await callback_query.message.answer(
            LEXICON["play_prompt"],
            reply_markup=game_menu_keyboard()
        )
        await callback_query.answer()
