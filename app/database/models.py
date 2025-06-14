"""
Модели базы данных
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

Base = declarative_base()


class Application(Base):
    """Модель заявки на курс"""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)  # Telegram User ID
    username = Column(String(100), nullable=True)  # Telegram username
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    contact_time = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)  # Обработана ли заявка
    referred_by = Column(BigInteger, nullable=True)  # Кто пригласил
    
    def __repr__(self):
        return f"<Application({self.name}, {self.phone})>"


class UnfinishedApplication(Base):
    """Модель незавершенной заявки"""
    __tablename__ = 'unfinished_applications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    current_step = Column(String(50), nullable=False)  # Текущий шаг
    data = Column(Text, nullable=True)  # JSON с введенными данными
    created_at = Column(DateTime, default=datetime.utcnow)
    reminder_sent = Column(Boolean, default=False)  # Отправлено ли напоминание
    
    def __repr__(self):
        return f"<UnfinishedApplication({self.user_id}, {self.current_step})>"


class Review(Base):
    """Модель отзывов"""
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)
    profit = Column(String(50), nullable=True)  # Заработок
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Review({self.name}, {self.country})>"


class Referral(Base):
    """Модель реферальной системы"""
    __tablename__ = 'referrals'
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(BigInteger, nullable=False)  # Кто пригласил
    referred_id = Column(BigInteger, nullable=False)  # Кого пригласили
    created_at = Column(DateTime, default=datetime.utcnow)
    bonus_paid = Column(Boolean, default=False)  # Выплачен ли бонус
    
    def __repr__(self):
        return f"<Referral({self.referrer_id} -> {self.referred_id})>"


# Создаём движок базы данных
engine = create_async_engine(DATABASE_URL, echo=False)

# Создаём фабрику сессий
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Получить сессию базы данных"""
    async with async_session() as session:
        yield session


class Buyer(Base):
    """Модель байера (рекламщика)"""
    __tablename__ = 'buyers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    telegram_username = Column(String(100), nullable=True)
    telegram_id = Column(BigInteger, nullable=True)
    source_type = Column(String(50), nullable=False)  # facebook, google, push и т.д.
    buyer_code = Column(String(50), unique=True, nullable=False)  # Уникальный код байера
    
    # Настройки для разных платформ
    fb_pixel_id = Column(String(100), nullable=True)
    fb_access_token = Column(Text, nullable=True)
    google_conversion_id = Column(String(100), nullable=True)
    google_conversion_label = Column(String(100), nullable=True)
    postback_url = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Статистика
    total_leads = Column(Integer, default=0)
    total_applications = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Buyer({self.name}, {self.source_type})>"


class PostbackLog(Base):
    """Лог отправки postback"""
    __tablename__ = 'postback_logs'
    
    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey('buyers.id'))
    application_id = Column(Integer, ForeignKey('applications.id'))
    status = Column(String(20))  # success, failed, retry
    response_code = Column(Integer, nullable=True)
    response_text = Column(Text, nullable=True)
    attempt = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PostbackLog({self.buyer_id}, {self.status})>"


class AdminUser(Base):
    """Модель админов"""
    __tablename__ = 'admin_users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    full_name = Column(String(200), nullable=True)
    role = Column(String(50), default='viewer')  # owner, admin, manager, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_action_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AdminUser({self.username}, {self.role})>"
