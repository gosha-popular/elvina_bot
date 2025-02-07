from aiogram.fsm.state import State, StatesGroup

from loader import QUERY


class Interview(StatesGroup):
    name = State()
    query = [State() for key in QUERY]
    phone = State()

class Reference(StatesGroup):
    view = State()