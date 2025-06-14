"""
Регистрация обработчиков админ-панели
"""
from aiogram import Dispatcher

from .main import router as main_router
from .dashboard import router as dashboard_router
from .analytics import router as analytics_router
from .buyers import router as buyers_router
from .system import router as system_router


def register_admin_handlers(dp: Dispatcher):
    """Регистрирует все обработчики админки"""
    dp.include_router(main_router)
    dp.include_router(dashboard_router)
    dp.include_router(analytics_router)
    dp.include_router(buyers_router)
    dp.include_router(system_router)
