"""
Запросы к базе данных
"""
import json
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Application, UnfinishedApplication, Review, async_session, Referral
from datetime import datetime, timedelta
from typing import Optional, List


async def create_application(
    user_id: int,
    username: Optional[str],
    name: str,
    country: str,
    phone: str,
    contact_time: str,
    referred_by: Optional[int] = None
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
            created_at=datetime.utcnow(),
            referred_by=referred_by
        )
        session.add(application)
        
        # Удаляем незавершенную заявку, если была
        unfinished = await session.execute(
            select(UnfinishedApplication).where(UnfinishedApplication.user_id == user_id)
        )
        unfinished_app = unfinished.scalar_one_or_none()
        if unfinished_app:
            await session.delete(unfinished_app)
        
        await session.commit()
        await session.refresh(application)
        
        # Если есть реферер, сохраняем связь
        if referred_by:
            referral = Referral(
                referrer_id=referred_by,
                referred_id=user_id
            )
            session.add(referral)
            await session.commit()
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


async def save_unfinished_application(
    user_id: int,
    username: Optional[str],
    current_step: str,
    data: dict
) -> UnfinishedApplication:
    """Сохранить незавершенную заявку"""
    async with async_session() as session:
        # Проверяем, есть ли уже незавершенная заявка
        result = await session.execute(
            select(UnfinishedApplication).where(UnfinishedApplication.user_id == user_id)
        )
        unfinished = result.scalar_one_or_none()
        
        if unfinished:
            # Обновляем существующую
            unfinished.current_step = current_step
            unfinished.data = json.dumps(data, ensure_ascii=False)
        else:
            # Создаем новую
            unfinished = UnfinishedApplication(
                user_id=user_id,
                username=username,
                current_step=current_step,
                data=json.dumps(data, ensure_ascii=False)
            )
            session.add(unfinished)
        
        await session.commit()
        return unfinished


async def get_unfinished_applications_for_reminder() -> List[UnfinishedApplication]:
    """Получить незавершенные заявки для напоминания"""
    async with async_session() as session:
        # Заявки старше 30 минут, которым не отправлено напоминание
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
        
        result = await session.execute(
            select(UnfinishedApplication).where(
                and_(
                    UnfinishedApplication.created_at <= thirty_minutes_ago,
                    UnfinishedApplication.reminder_sent == False
                )
            )
        )
        return result.scalars().all()


async def mark_reminder_sent(user_id: int):
    """Отметить, что напоминание отправлено"""
    async with async_session() as session:
        result = await session.execute(
            select(UnfinishedApplication).where(UnfinishedApplication.user_id == user_id)
        )
        unfinished = result.scalar_one_or_none()
        if unfinished:
            unfinished.reminder_sent = True
            await session.commit()


async def get_recent_applications_count(hours: int = 1) -> int:
    """Получить количество заявок за последние N часов"""
    async with async_session() as session:
        time_ago = datetime.utcnow() - timedelta(hours=hours)
        result = await session.execute(
            select(func.count(Application.id)).where(
                Application.created_at >= time_ago
            )
        )
        return result.scalar() or 0


async def get_recent_applications(limit: int = 5) -> List[Application]:
    """Получить последние заявки"""
    async with async_session() as session:
        result = await session.execute(
            select(Application)
            .order_by(Application.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


async def get_random_reviews(limit: int = 3) -> List[Review]:
    """Получить случайные отзывы"""
    async with async_session() as session:
        result = await session.execute(
            select(Review)
            .where(Review.is_active == True)
            .order_by(func.random())
            .limit(limit)
        )
        return result.scalars().all()


async def add_review(name: str, country: str, text: str, profit: Optional[str] = None) -> Review:
    """Добавить отзыв"""
    async with async_session() as session:
        review = Review(
            name=name,
            country=country,
            text=text,
            profit=profit
        )
        session.add(review)
        await session.commit()
        return review


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


async def get_all_applications(limit: int = 100) -> List[Application]:
    """Получить все заявки"""
    async with async_session() as session:
        result = await session.execute(
            select(Application)
            .order_by(Application.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


async def get_unprocessed_applications() -> List[Application]:
    """Получить необработанные заявки"""
    async with async_session() as session:
        result = await session.execute(
            select(Application)
            .where(Application.is_processed == False)
            .order_by(Application.created_at.desc())
        )
        return result.scalars().all()


async def save_referral(referrer_id: int, referred_id: int):
    """Сохранить реферальную связь"""
    async with async_session() as session:
        referral = Referral(
            referrer_id=referrer_id,
            referred_id=referred_id
        )
        session.add(referral)
        await session.commit()
        return referral


async def get_user_referrals_count(user_id: int) -> int:
    """Получить количество приглашенных пользователей"""
    async with async_session() as session:
        result = await session.execute(
            select(func.count(Referral.id)).where(
                Referral.referrer_id == user_id
            )
        )
        return result.scalar() or 0


async def get_referrer_by_user_id(user_id: int) -> Optional[int]:
    """Получить ID пригласившего по ID пользователя"""
    async with async_session() as session:
        result = await session.execute(
            select(Application.referred_by).where(
                Application.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
