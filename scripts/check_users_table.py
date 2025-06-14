"""
Проверка и исправление таблицы users
"""
import asyncio
from sqlalchemy import text
from app.database.models import engine

async def check_and_fix_users():
    async with engine.begin() as conn:
        # Проверяем структуру таблицы users
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print("=== Текущие колонки в таблице users ===")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Проверяем, есть ли колонка user_id
        column_names = [col[0] for col in columns]
        
        if 'user_id' not in column_names:
            print("\n❌ Колонка user_id отсутствует! Добавляем...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN user_id BIGINT UNIQUE NOT NULL DEFAULT 0
            """))
            print("✅ Колонка user_id добавлена")
        else:
            print("\n✅ Колонка user_id существует")

if __name__ == "__main__":
    asyncio.run(check_and_fix_users())
