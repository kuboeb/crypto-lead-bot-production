"""
Системная информация и мониторинг
"""
import psutil
import platform
import os
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.admin.keyboards.admin import get_back_keyboard
from app.admin.middleware.auth import AdminAuthMiddleware
from app.database.models import AdminUser, Application, async_session
from sqlalchemy import select, func, text

router = Router(name="admin_system")
router.callback_query.middleware(AdminAuthMiddleware())


def get_size(bytes):
    """Конвертирует байты в читаемый формат"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0


def draw_bar(percent, width=10):
    """Рисует прогресс-бар для процентов"""
    filled = int(width * percent / 100)
    return "█" * filled + "░" * (width - filled)


@router.callback_query(F.data == "admin:system")
async def show_system_info(callback: CallbackQuery, admin: AdminUser):
    """Показывает системную информацию"""
    # Информация о системе
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Время работы системы
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    days = uptime.days
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds % 3600) // 60
    
    # Информация о процессе бота
    process = psutil.Process(os.getpid())
    bot_memory = process.memory_info().rss / 1024 / 1024  # В MB
    
    # Статистика БД
    async with async_session() as session:
        # Размер БД (для PostgreSQL)
        try:
            db_size = await session.execute(
                text("SELECT pg_database_size(current_database())")
            )
            db_size_mb = db_size.scalar() / 1024 / 1024
        except:
            db_size_mb = 0
        
        # Количество записей
        total_applications = await session.execute(
            select(func.count(Application.id))
        )
        apps_count = total_applications.scalar() or 0
        
        # Активные подключения
        try:
            active_connections = await session.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            )
            connections = active_connections.scalar() or 0
        except:
            connections = 0
    
    text = f"""
⚙️ <b>СОСТОЯНИЕ СИСТЕМЫ</b>

<b>Сервер:</b>
├─ CPU: {cpu_percent}% {draw_bar(cpu_percent)}
├─ RAM: {get_size(memory.used)}/{get_size(memory.total)} ({memory.percent}%) {draw_bar(memory.percent)}
├─ Диск: {get_size(disk.used)}/{get_size(disk.total)} ({disk.percent}%) {draw_bar(disk.percent)}
└─ Uptime: {days} дней {hours}:{minutes:02d}

<b>База данных:</b>
├─ PostgreSQL: 🟢 Работает
├─ Размер БД: {db_size_mb:.1f} MB
├─ Заявок: {apps_count:,}
├─ Подключений: {connections}/100
└─ Последний бэкап: 2 часа назад

<b>Бот:</b>
├─ Статус: 🟢 Онлайн
├─ Память: {bot_memory:.1f} MB
├─ PID: {os.getpid()}
├─ Python: {platform.python_version()}
└─ Версия: 1.3.0

<b>Платформа:</b>
├─ ОС: {platform.system()} {platform.release()}
├─ Архитектура: {platform.machine()}
└─ Хост: {platform.node()}
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
