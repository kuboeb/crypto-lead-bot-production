"""
Модуль для отслеживания действий пользователей
"""
import uuid
from datetime import datetime
from typing import Optional

from app.database.models import UserAction, async_session
from aiogram.types import User as TelegramUser


class ActionTracker:
    """Класс для трекинга действий пользователей"""
    
    # Словарь активных сессий {user_id: (session_id, start_time)}
    _sessions = {}
    
    @classmethod
    async def track_action(
        cls,
        user: TelegramUser,
        action_type: str,
        action_value: Optional[str] = None,
        step_name: Optional[str] = None,
        previous_action: Optional[str] = None
    ):
        """Отслеживает действие пользователя"""
        user_id = user.id
        
        # Создаем или получаем сессию
        if user_id not in cls._sessions or action_type == "start":
            session_id = str(uuid.uuid4())
            cls._sessions[user_id] = (session_id, datetime.utcnow())
        else:
            session_id, start_time = cls._sessions[user_id]
        
        # Вычисляем время от начала сессии
        if action_type != "start":
            _, start_time = cls._sessions.get(user_id, (None, datetime.utcnow()))
            time_since_start = int((datetime.utcnow() - start_time).total_seconds())
        else:
            time_since_start = 0
        
        # Сохраняем в БД
        async with async_session() as session:
            action = UserAction(
                user_id=user_id,
                action_type=action_type,
                action_value=action_value,
                step_name=step_name,
                session_id=session_id,
                time_since_start=time_since_start,
                previous_action=previous_action,
                device_info=f"tg_{user.language_code or 'unknown'}"
            )
            session.add(action)
            await session.commit()
    
    @classmethod
    def get_session_id(cls, user_id: int) -> Optional[str]:
        """Получает ID текущей сессии пользователя"""
        if user_id in cls._sessions:
            return cls._sessions[user_id][0]
        return None
