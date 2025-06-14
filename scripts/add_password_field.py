"""
Добавление поля password_hash в таблицу admin_users
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import engine
from sqlalchemy import text

async def add_password_field():
    """Добавляет поле password_hash"""
    async with engine.begin() as conn:
        try:
            await conn.execute(text("""
                ALTER TABLE admin_users 
                ADD COLUMN IF NOT EXISTS password_hash VARCHAR(200)
            """))
            print("✅ Поле password_hash добавлено")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(add_password_field())
