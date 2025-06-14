"""
Добавление тестовых данных
"""
import asyncio
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import Application, Buyer, UserAction, async_session
from sqlalchemy import select


async def add_test_data():
    """Добавляет тестовые данные"""
    async with async_session() as session:
        # Добавляем тестового байера
        buyer = Buyer(
            name="Тестовый байер",
            source_type="facebook",
            buyer_code="test_buyer_001",
            is_active=True,
            total_leads=0,
            total_applications=0
        )
        session.add(buyer)
        
        # Добавляем тестовые заявки
        countries = ["Россия", "Казахстан", "Беларусь", "Украина"]
        times = ["10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]
        
        for i in range(50):
            # Случайная дата за последние 7 дней
            days_ago = random.randint(0, 7)
            created_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            application = Application(
                user_id=1000000 + i,
                name=f"Тестовый пользователь {i}",
                country=random.choice(countries),
                phone=f"+7900000{i:04d}",
                contact_time=random.choice(times),
                created_at=created_at,
                is_processed=random.choice([True, False]),
                referred_by="test_buyer_001" if random.random() > 0.5 else None
            )
            session.add(application)
            
            # Добавляем действия пользователя
            user_id = 1000000 + i
            session_id = f"session_{i}"
            
            # Симулируем воронку
            actions = [
                ("start", "funnel_start", 0),
                ("menu_view", "funnel_menu_opened", 5),
                ("button_click", "funnel_apply_clicked", 10),
                ("form_start", "funnel_form_started", 15),
                ("input_name", "funnel_name_entered", 30),
                ("select_country", "funnel_country_entered", 45),
                ("input_phone", "funnel_phone_entered", 60),
                ("select_time", "funnel_time_selected", 75),
                ("form_complete", "funnel_completed", 90),
            ]
            
            # Случайное количество пройденных шагов
            steps_completed = random.randint(1, len(actions))
            
            for j, (action_type, step_name, time_offset) in enumerate(actions[:steps_completed]):
                action = UserAction(
                    user_id=user_id,
                    action_type=action_type,
                    step_name=step_name,
                    session_id=session_id,
                    created_at=created_at + timedelta(seconds=time_offset),
                    time_since_start=time_offset
                )
                session.add(action)
        
        await session.commit()
        print("✅ Тестовые данные добавлены")
        print("- 1 байер")
        print("- 50 заявок")
        print("- Действия пользователей для воронки")


if __name__ == "__main__":
    asyncio.run(add_test_data())
