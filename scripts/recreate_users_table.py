"""
Пересоздание таблицы users с правильной структурой
"""
import asyncio
from sqlalchemy import text
from app.database.models import engine

async def recreate_users_table():
    async with engine.begin() as conn:
        print("Удаляем старую таблицу users...")
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        
        print("Создаем новую таблицу users...")
        await conn.execute(text("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(100),
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_blocked BOOLEAN DEFAULT FALSE
            )
        """))
        
        print("✅ Таблица users пересоздана")
        
        # Проверяем структуру
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        
        print("\nНовая структура таблицы:")
        for col in result:
            print(f"  - {col[0]}: {col[1]}")

if __name__ == "__main__":
    asyncio.run(recreate_users_table())
