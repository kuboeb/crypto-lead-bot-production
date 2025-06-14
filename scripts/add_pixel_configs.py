"""
Добавление таблицы конфигураций пикселей
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import engine, Base


async def add_pixel_configs_table():
    """Создает таблицу конфигураций пикселей"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблица buyer_pixel_configs создана")


if __name__ == "__main__":
    asyncio.run(add_pixel_configs_table())
