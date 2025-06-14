"""
Модели базы данных
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, Text
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
