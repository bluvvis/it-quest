from aiogram.filters.state import StatesGroup, State

class QuestStates(StatesGroup):
    waiting_for_start = State()
    find_ip = State()
    find_city = State()
    find_password = State()
    find_hidden_button = State()
