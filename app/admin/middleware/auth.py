"""
Middleware для проверки прав доступа к админке
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from app.database.models import async_session, AdminUser
from sqlalchemy import select

class AdminAuthMiddleware(BaseMiddleware):
    """Проверка прав доступа к админке"""
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        
        # Проверяем, является ли пользователь админом
        async with async_session() as session:
            result = await session.execute(
                select(AdminUser).where(
                    AdminUser.telegram_id == user_id,
                    AdminUser.is_active == True
                )
            )
            admin = result.scalar_one_or_none()
            
            if not admin:
                if isinstance(event, Message):
                    await event.answer("⛔ У вас нет доступа к админ-панели!")
                else:
                    await event.answer("⛔ Доступ запрещен!", show_alert=True)
                return
            
            # Добавляем админа в данные для использования в хендлерах
            data['admin'] = admin
            
            # Обновляем время последнего действия
            admin.last_action_at = datetime.utcnow()
            await session.commit()
            
        return await handler(event, data)


def check_admin_role(required_role: str):
    """Декоратор для проверки роли админа"""
    def decorator(func):
        async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
            admin = kwargs.get('admin')
            
            # Иерархия ролей: owner > admin > manager > viewer
            role_hierarchy = {
                'viewer': 0,
                'manager': 1,
                'admin': 2,
                'owner': 3
            }
            
            if role_hierarchy.get(admin.role, 0) < role_hierarchy.get(required_role, 0):
                if isinstance(event, Message):
                    await event.answer(f"⛔ Требуется роль: {required_role}")
                else:
                    await event.answer(f"⛔ Недостаточно прав!", show_alert=True)
                return
                
            return await func(event, *args, **kwargs)
        return wrapper
    return decorator
