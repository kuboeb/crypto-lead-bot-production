"""
Проверка модели Buyer
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import Buyer, async_session
from sqlalchemy import inspect


async def check_buyer_model():
    """Проверяет модель Buyer"""
    async with async_session() as session:
        # Получаем информацию о таблице
        inspector = inspect(session.bind)
        
        # Получаем колонки таблицы buyers
        columns = await session.run_sync(lambda sync_session: inspector.get_columns('buyers'))
        
        print("Колонки таблицы buyers:")
        for col in columns:
            print(f"- {col['name']}: {col['type']}")


if __name__ == "__main__":
    asyncio.run(check_buyer_model())
