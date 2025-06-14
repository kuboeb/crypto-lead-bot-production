from sqlalchemy import Float
"""
Модели базы данных
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
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
    role = Column(String(50), default='viewer')
    password_hash = Column(String(200), nullable=True)  # owner, admin, manager, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_action_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AdminUser({self.username}, {self.role})>"



class UserAction(Base):
    """Модель для отслеживания действий пользователей"""
    __tablename__ = 'user_actions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    action_type = Column(String(50), nullable=False)  # start, menu_view, button_click, etc
    action_value = Column(String(200), nullable=True)  # какая кнопка, какое меню и т.д.
    step_name = Column(String(100), nullable=True)  # название шага воронки
    session_id = Column(String(100), nullable=True)  # для группировки действий в сессии
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Дополнительные поля для аналитики
    time_since_start = Column(Integer, nullable=True)  # секунды от начала сессии
    previous_action = Column(String(50), nullable=True)
    device_info = Column(String(200), nullable=True)


class FunnelSnapshot(Base):
    """Снимки воронки для быстрой загрузки"""
    __tablename__ = 'funnel_snapshots'
    
    id = Column(Integer, primary_key=True)
    snapshot_time = Column(DateTime, default=datetime.utcnow)
    total_users = Column(Integer, default=0)
    
    # Детальные шаги воронки
    step_start = Column(Integer, default=0)
    step_menu_opened = Column(Integer, default=0)
    step_apply_clicked = Column(Integer, default=0)
    step_form_started = Column(Integer, default=0)
    step_name_entered = Column(Integer, default=0)
    step_country_entered = Column(Integer, default=0)
    step_phone_entered = Column(Integer, default=0)
    step_time_selected = Column(Integer, default=0)
    step_completed = Column(Integer, default=0)
    
    # Процент отвала на каждом шаге
    drop_after_start = Column(Float, default=0)
    drop_after_menu = Column(Float, default=0)
    drop_after_apply = Column(Float, default=0)
    drop_after_form_start = Column(Float, default=0)
    drop_after_name = Column(Float, default=0)
    drop_after_country = Column(Float, default=0)
    drop_after_phone = Column(Float, default=0)
    drop_after_time = Column(Float, default=0)


class BuyerPixelConfig(Base):
    """Конфигурация пикселей и постбэков для байера"""
    __tablename__ = 'buyer_pixel_configs'
    
    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey('buyers.id'))
    
    # Facebook CAPI
    fb_pixel_id = Column(String(100), nullable=True)
    fb_access_token = Column(Text, nullable=True)
    fb_test_event_code = Column(String(50), nullable=True)
    
    # Google Ads
    google_conversion_id = Column(String(100), nullable=True)
    google_conversion_label = Column(String(100), nullable=True)
    google_api_version = Column(String(20), default='v13')
    
    # Telegram Ads
    telegram_token = Column(Text, nullable=True)
    
    # PropellerAds
    propeller_auth_token = Column(Text, nullable=True)
    propeller_offer_id = Column(String(100), nullable=True)
    
    # RichAds
    richads_campaign_id = Column(String(100), nullable=True)
    richads_auth_token = Column(Text, nullable=True)
    
    # EvaDav
    evadav_campaign_id = Column(String(100), nullable=True)
    evadav_postback_url = Column(Text, nullable=True)
    
    # PushHouse
    pushhouse_source_id = Column(String(100), nullable=True)
    pushhouse_external_id = Column(String(100), nullable=True)
    
    # OnClick
    onclick_campaign_uuid = Column(String(100), nullable=True)
    onclick_source_id = Column(String(100), nullable=True)
    
    # Общие настройки
    send_test_events = Column(Boolean, default=True)
    retry_failed = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с байером
    buyer = relationship("Buyer", back_populates="pixel_config", uselist=False)


# Добавляем связь в модель Buyer
Buyer.pixel_config = relationship("BuyerPixelConfig", back_populates="buyer", uselist=False)
