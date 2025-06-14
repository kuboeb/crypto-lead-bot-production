#!/usr/bin/env python3
"""
Главный файл запуска бота
"""
import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import BOT_TOKEN
from app.handlers import register_all_handlers
from app.database.models import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция"""
    # Инициализируем БД
    logger.info("Инициализация базы данных...")
    await init_db()
    
    # Создаём бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    
    # Создаём диспетчер
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрируем обработчики
    register_all_handlers(dp)
    
    # Запускаем бота
    try:
        logger.info("Бот запущен!")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
