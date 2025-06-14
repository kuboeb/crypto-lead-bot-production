"""
Обновление пароля для админа
"""
import asyncio
import sys
from pathlib import Path
from passlib.context import CryptContext

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import AdminUser, async_session
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def update_admin_password():
    """Устанавливает пароль admin для пользователя admin"""
    async with async_session() as session:
        # Получаем админа
        result = await session.execute(
            select(AdminUser).where(AdminUser.role == "owner")
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            # Устанавливаем пароль "admin"
            admin.password_hash = pwd_context.hash("admin")
            await session.commit()
            print(f"✅ Пароль обновлен для {admin.username}")
            print(f"Логин: {admin.username}")
            print(f"Пароль: admin")
        else:
            print("❌ Админ не найден")

if __name__ == "__main__":
    asyncio.run(update_admin_password())
