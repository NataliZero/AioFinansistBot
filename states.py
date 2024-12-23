from aiogram.fsm.state import State, StatesGroup

# Определяем состояния для работы с финансами
class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()
