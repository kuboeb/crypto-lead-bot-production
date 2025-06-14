"""
Запросы к базе данных
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Application, async_session
from datetime import datetime
from typing import Optional


async def create_application(
    user_id: int,
    username: Optional[str],
    name: str,
    country: str,
    phone: str,
    contact_time: str
) -> Application:
    """Создать новую заявку"""
    async with async_session() as session:
        application = Application(
            user_id=user_id,
            username=username,
            name=name,
            country=country,
            phone=phone,
            contact_time=contact_time,
            created_at=datetime.utcnow()
        )
        session.add(application)
        await session.commit()
        await session.refresh(application)
        return application


async def get_application_by_user_id(user_id: int) -> Optional[Application]:
    """Получить заявку по user_id"""
    async with async_session() as session:
        result = await session.execute(
            select(Application).where(Application.user_id == user_id)
        )
        return result.scalar_one_or_none()


async def user_has_application(user_id: int) -> bool:
    """Проверить, есть ли у пользователя заявка"""
    application = await get_application_by_user_id(user_id)
    return application is not None


async def mark_application_processed(user_id: int) -> bool:
    """Отметить заявку как обработанную"""
    async with async_session() as session:
        result = await session.execute(
            select(Application).where(Application.user_id == user_id)
        )
        application = result.scalar_one_or_none()
        if application:
            application.is_processed = True
            await session.commit()
            return True
        return False


async def get_all_applications(limit: int = 100) -> list[Application]:
    """Получить все заявки"""
    async with async_session() as session:
        result = await session.execute(
            select(Application)
            .order_by(Application.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


async def get_unprocessed_applications() -> list[Application]:
    """Получить необработанные заявки"""
    async with async_session() as session:
        result = await session.execute(
            select(Application)
            .where(Application.is_processed == False)
            .order_by(Application.created_at.desc())
        )
        return result.scalars().all()
