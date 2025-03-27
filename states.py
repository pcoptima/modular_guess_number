from aiogram.fsm.state import State, StatesGroup


class GameStates(StatesGroup):
    out_game = State()
    game = State()
    set_range = State()
    set_time = State()
    set_attempts = State()
