from aiogram.fsm.state import StatesGroup, State


class EnterPassword(StatesGroup):
    enter_password = State()
