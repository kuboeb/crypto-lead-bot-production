"""
Тест подключения к БД
"""
import asyncio
from sqlalchemy import text
from app.database.models import engine, async_session, User

async def test_connection():
    print("🔍 Тестируем подключение к БД...")
    
    try:
        # Тест 1: Простой запрос
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Подключение к БД работает")
            
        # Тест 2: Проверка таблицы users
        async with async_session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✅ Таблица users доступна. Записей: {count}")
            
        # Тест 3: Создание тестового пользователя
        async with async_session() as session:
            test_user = User(
                user_id=123456789,
                username="test_user",
                first_name="Test",
                last_name="User"
            )
            session.add(test_user)
            await session.commit()
            print("✅ Создание пользователя работает")
            
            # Удаляем тестового пользователя
            await session.execute(text("DELETE FROM users WHERE user_id = 123456789"))
            await session.commit()
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nПопробуйте выполнить:")
        print("sudo -u postgres psql crypto_leads -c 'GRANT ALL ON ALL TABLES IN SCHEMA public TO crypto_user;'")

if __name__ == "__main__":
    asyncio.run(test_connection())
