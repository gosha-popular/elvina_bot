from aiogram.fsm.state import State, StatesGroup



class Interview(StatesGroup):
    name = State()
    question = State()
    phone = State()

class Reference(StatesGroup):
    view = State()