"""
Скрипт для добавления админа в базу данных
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import init_db, AdminUser, async_session
from app.config import ADMIN_ID


async def add_admin():
    """Добавляет владельца как админа"""
    await init_db()
    
    async with async_session() as session:
        # Проверяем, есть ли уже админ
        existing = await session.get(AdminUser, {'telegram_id': ADMIN_ID})
        
        if existing:
            print(f"✅ Админ с ID {ADMIN_ID} уже существует")
            return
        
        # Создаем админа
        admin = AdminUser(
            telegram_id=ADMIN_ID,
            username="admin",
            full_name="Главный администратор",
            role="owner",
            is_active=True
        )
        
        session.add(admin)
        await session.commit()
        
        print(f"✅ Админ успешно добавлен!")
        print(f"Telegram ID: {ADMIN_ID}")
        print(f"Роль: owner")
        print(f"\nТеперь вы можете использовать команду /admin в боте")


if __name__ == "__main__":
    asyncio.run(add_admin())
