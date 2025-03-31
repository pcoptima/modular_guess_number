from aiogram import types


def start_menu_keyboard():
    kb = [
        [
            types.InlineKeyboardButton(
                text='Правила игры', callback_data='rules')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def settings_menu_keyboard():
    kb = [
        [
            types.InlineKeyboardButton(
                text="Диапазон чисел", callback_data="set_range"),
            types.InlineKeyboardButton(text="Время", callback_data="set_time"),
            types.InlineKeyboardButton(
                text="Попыток", callback_data="set_attempts")
        ],
        [
            types.InlineKeyboardButton(
                text="Мои настройки", callback_data="my_settings")
        ],
        [
            types.InlineKeyboardButton(text="Играть", callback_data="play")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def my_settings_menu_keyboard():
    kb = [
        [
            types.InlineKeyboardButton(
                text="Диапазон чисел", callback_data="set_range"),
            types.InlineKeyboardButton(text="Время", callback_data="set_time"),
            types.InlineKeyboardButton(
                text="Попыток", callback_data="set_attempts")
        ],
        [
            types.InlineKeyboardButton(text="Играть", callback_data="play")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def main_menu_keyboard():
    kb = [
        [
            types.InlineKeyboardButton(text="Играть", callback_data="play")
        ],
        [
            types.InlineKeyboardButton(
                text="Статистика", callback_data="stats"),
            types.InlineKeyboardButton(
                text="Настройка игры", callback_data="settings")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def game_menu_keyboard():
    kb = [
        [
            types.InlineKeyboardButton(
                text="Настройка игры", callback_data="settings"),
            types.InlineKeyboardButton(
                text="Мои настройки", callback_data="my_settings"),
            types.InlineKeyboardButton(
                text="Статистика", callback_data="stats")
        ],
        [
            types.InlineKeyboardButton(
                text="Прервать", callback_data="cancel")
        ],
        [
            types.InlineKeyboardButton(
                text="Играть", callback_data="play")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def in_game_menu_keyboard():
    kb = [
        [
            types.InlineKeyboardButton(
                text="Настройка игры", callback_data="settings"),
            types.InlineKeyboardButton(
                text="Мои настройки", callback_data="my_settings"),
            types.InlineKeyboardButton(
                text="Статистика", callback_data="stats")
        ],
        [
            types.InlineKeyboardButton(
                text="Прервать", callback_data="cancel")
        ],
        [
            types.InlineKeyboardButton(
                text="Правила игры", callback_data="rules")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard
