"""
Клавиатуры для админ-панели
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню админки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔴 LIVE Dashboard", callback_data="admin:dashboard")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Воронка продаж", callback_data="admin:funnel"),
        InlineKeyboardButton(text="👥 Байеры", callback_data="admin:buyers")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Заявки", callback_data="admin:applications"),
        InlineKeyboardButton(text="💾 Экспорт", callback_data="admin:export")
    )
    builder.row(
        InlineKeyboardButton(text="🔐 Безопасность", callback_data="admin:security"),
        InlineKeyboardButton(text="⚙️ Система", callback_data="admin:system")
    )
    
    return builder.as_markup()


def get_buyers_keyboard() -> InlineKeyboardMarkup:
    """Меню управления байерами"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Добавить байера", callback_data="admin:add_buyer")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Статистика байеров", callback_data="admin:buyers_stats")
    )
    builder.row(
        InlineKeyboardButton(text="↩️ Назад", callback_data="admin:main")
    )
    
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="↩️ Назад", callback_data="admin:main")
    )
    return builder.as_markup()


def get_buyer_sources_keyboard() -> InlineKeyboardMarkup:
    """Выбор источника трафика для байера"""
    builder = InlineKeyboardBuilder()
    
    sources = [
        ("Facebook", "facebook"),
        ("Google Ads", "google"),
        ("Telegram Ads", "telegram"),
        ("PropellerAds", "propeller"),
        ("RichAds", "richads"),
        ("EvaDav", "evadav"),
        ("PushHouse", "pushhouse"),
        ("OnClick", "onclick"),
        ("Другой", "custom")
    ]
    
    for name, code in sources:
        builder.row(
            InlineKeyboardButton(
                text=name, 
                callback_data=f"admin:buyer_source:{code}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="admin:buyers")
    )
    
    return builder.as_markup()


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data="admin:confirm"),
        InlineKeyboardButton(text="❌ Нет", callback_data="admin:cancel")
    )
    
    return builder.as_markup()
