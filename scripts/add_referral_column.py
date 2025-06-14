"""
Скрипт для добавления колонки referred_by в таблицу applications
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import engine
from sqlalchemy import text

async def add_referred_by_column():
    """Добавляет колонку referred_by в таблицу applications"""
    async with engine.begin() as conn:
        try:
            # Добавляем колонку referred_by
            await conn.execute(text("""
                ALTER TABLE applications 
                ADD COLUMN IF NOT EXISTS referred_by BIGINT
            """))
            print("✅ Колонка referred_by добавлена в таблицу applications")
            
            # Создаем таблицу referrals если её нет
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id SERIAL PRIMARY KEY,
                    referrer_id BIGINT NOT NULL,
                    referred_id BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    bonus_paid BOOLEAN DEFAULT FALSE
                )
            """))
            print("✅ Таблица referrals создана")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(add_referred_by_column())
