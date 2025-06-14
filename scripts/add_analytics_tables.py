"""
Добавление таблиц для аналитики
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import engine, Base
from sqlalchemy import text


async def add_analytics_tables():
    """Создает новые таблицы для аналитики"""
    async with engine.begin() as conn:
        # Создаем таблицы
        await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Таблицы для аналитики созданы")


if __name__ == "__main__":
    asyncio.run(add_analytics_tables())
