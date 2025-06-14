"""
Проверка структуры таблицы applications
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import async_session
from sqlalchemy import text


async def check_table():
    """Проверяет структуру таблицы"""
    async with async_session() as session:
        # Получаем структуру таблицы
        result = await session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'applications'
            ORDER BY ordinal_position
        """))
        
        print("Структура таблицы applications:")
        for row in result:
            print(f"- {row.column_name}: {row.data_type}")


if __name__ == "__main__":
    asyncio.run(check_table())
