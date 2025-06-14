"""
Полное исправление структуры БД и прав доступа
"""
import asyncio
import subprocess
from sqlalchemy import text
from app.database.models import engine

async def fix_database():
    """Исправляет все проблемы с БД"""
    print("🔧 Начинаем исправление базы данных...")
    
    # Выполняем SQL команды через psql с правами postgres
    sql_commands = """
    -- Удаляем старую таблицу users если есть
    DROP TABLE IF EXISTS users CASCADE;

    -- Создаем таблицу users с правильной структурой
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        user_id BIGINT UNIQUE NOT NULL,
        username VARCHAR(100),
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_blocked BOOLEAN DEFAULT FALSE
    );

    -- Даем все права пользователю crypto_user
    GRANT ALL PRIVILEGES ON TABLE users TO crypto_user;
    GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO crypto_user;
    
    -- Проверяем другие таблицы и даем права
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crypto_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crypto_user;
    """
    
    # Выполняем через sudo
    process = subprocess.run(
        ['sudo', '-u', 'postgres', 'psql', 'crypto_leads', '-c', sql_commands],
        capture_output=True,
        text=True
    )
    
    if process.returncode == 0:
        print("✅ База данных исправлена!")
        print("\nСтруктура таблицы users:")
        
        # Проверяем структуру
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """))
            
            for col in result:
                print(f"  - {col[0]}: {col[1]}")
    else:
        print(f"❌ Ошибка: {process.stderr}")

if __name__ == "__main__":
    asyncio.run(fix_database())
