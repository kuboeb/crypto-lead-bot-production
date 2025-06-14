"""
Добавление простых тестовых данных
"""
import asyncio
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.models import Application, Buyer, UserAction, async_session


async def add_test_data():
    """Добавляет тестовые данные"""
    async with async_session() as session:
        # Сначала добавим байера
        buyer = Buyer(
            name="Тестовый байер Facebook",
            source_type="facebook",
            buyer_code="test_fb_001",
            is_active=True,
            total_leads=25,
            total_applications=20
        )
        session.add(buyer)
        await session.commit()
        
        print(f"✅ Байер создан с ID: {buyer.id}")
        
        # Теперь добавляем заявки
        countries = ["Россия", "Казахстан", "Беларусь", "Украина"]
        times = ["10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]
        
        for i in range(30):
            days_ago = random.randint(0, 7)
            created_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            application = Application(
                user_id=2000000 + i,
                name=f"Пользователь {i+1}",
                country=random.choice(countries),
                phone=f"+7999000{i:04d}",
                contact_time=random.choice(times),
                created_at=created_at,
                is_processed=random.choice([True, False]),
                referred_by="test_fb_001" if i % 2 == 0 else None
            )
            session.add(application)
        
        await session.commit()
        print("✅ 30 заявок добавлено")
        
        # Добавляем действия для воронки (последние 2 часа)
        base_time = datetime.utcnow() - timedelta(hours=2)
        
        for i in range(20):
            user_id = 3000000 + i
            session_id = f"session_{i}"
            start_time = base_time + timedelta(minutes=i*5)
            
            # Шаги воронки
            steps = [
                ("start", "funnel_start", 0),
                ("menu_view", "funnel_menu_opened", 10),
                ("button_click", "funnel_apply_clicked", 20),
                ("form_start", "funnel_form_started", 30),
                ("input_name", "funnel_name_entered", 60),
                ("select_country", "funnel_country_entered", 90),
                ("input_phone", "funnel_phone_entered", 120),
                ("select_time", "funnel_time_selected", 150),
                ("form_complete", "funnel_completed", 180),
            ]
            
            # Случайное количество шагов
            num_steps = random.randint(1, len(steps))
            
            for j in range(num_steps):
                action_type, step_name, time_offset = steps[j]
                
                action = UserAction(
                    user_id=user_id,
                    action_type=action_type,
                    step_name=step_name,
                    session_id=session_id,
                    created_at=start_time + timedelta(seconds=time_offset),
                    time_since_start=time_offset
                )
                session.add(action)
        
        await session.commit()
        print("✅ Действия пользователей добавлены")
        print("\nГотово! Теперь в админке должны появиться данные.")


if __name__ == "__main__":
    asyncio.run(add_test_data())
