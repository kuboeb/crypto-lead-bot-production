"""
Состояния для заявки на курс
"""
from aiogram.fsm.state import State, StatesGroup


class ApplicationStates(StatesGroup):
    """Состояния процесса подачи заявки"""
    
    # Ожидание данных от пользователя
    waiting_for_name = State()
    waiting_for_country = State()
    waiting_for_phone = State()
    waiting_for_contact_time = State()
