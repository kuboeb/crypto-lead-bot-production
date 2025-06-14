"""
Регистрация всех обработчиков
"""
from aiogram import Dispatcher

from .start import router as start_router
from .application import router as application_router
from .info import router as info_router
from .referral import router as referral_router


def register_all_handlers(dp: Dispatcher):
    """Регистрирует все обработчики"""
    # Важно: referral должен быть первым для обработки deep links
    dp.include_router(referral_router)
    dp.include_router(start_router)
    dp.include_router(application_router)
    dp.include_router(info_router)
