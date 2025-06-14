"""
Добавление базовых тестовых данных
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import Application, async_session
from datetime import datetime, timedelta
import random


async def add_test_data():
    """Добавляет базовые тестовые данные"""
    async with async_session() as session:
        # Добавляем простые заявки
        for i in range(10):
            app = Application(
                user_id=3000000 + i,
                name=f"Тест {i+1}",
                country="Россия",
                phone=f"+7999111{i:04d}",
                contact_time="10:00-12:00",
                created_at=datetime.utcnow() - timedelta(hours=i),
                is_processed=i % 2 == 0
            )
            session.add(app)
        
        await session.commit()
        print("✅ 10 тестовых заявок добавлено")


if __name__ == "__main__":
    asyncio.run(add_test_data())
