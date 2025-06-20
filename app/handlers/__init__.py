"""
Регистрация всех обработчиков
"""
from aiogram import Dispatcher

from .start import router as start_router
from .application import router as application_router
from .info import router as info_router
from .referral import router as referral_router
from .commands import router as commands_router


def register_all_handlers(dp: Dispatcher):
    """Регистрирует все обработчики"""
    dp.include_router(commands_router)
    dp.include_router(start_router)
    dp.include_router(application_router)
    dp.include_router(info_router)
    dp.include_router(referral_router)
