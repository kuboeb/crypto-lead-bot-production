"""
Клавиатуры для пользователей
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.config import CONTACT_TIMES


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура"""
    builder = InlineKeyboardBuilder()
    
    # Главная кнопка
    builder.row(
        InlineKeyboardButton(
            text="🚀 Записаться на курс",
            callback_data="start_application"
        )
    )
    
    # Информационные кнопки
    builder.row(
        InlineKeyboardButton(
            text="📚 Программа курса",
            callback_data="show_program"
        ),
        InlineKeyboardButton(
            text="💬 Отзывы",
            callback_data="show_reviews"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="❓ Частые вопросы",
            callback_data="show_faq"
        ),
        InlineKeyboardButton(
            text="💎 Почему крипто?",
            callback_data="show_why_crypto"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🛡 Гарантии",
            callback_data="show_guarantees"
        ),
        InlineKeyboardButton(
            text="👥 О нас",
            callback_data="show_about"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🌟 Истории успеха",
            callback_data="show_success_stories"
        )
    )
    
    return builder.as_markup()


def get_after_application_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после подачи заявки"""
    builder = InlineKeyboardBuilder()
    
    
    # Добавляем кнопку реферальной программы
    builder.row(
        InlineKeyboardButton(
            text="💰 Приведи друга - получи 50€",
            callback_data="show_referral_program"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📚 Программа курса",
            callback_data="show_program"
        ),
        InlineKeyboardButton(
            text="💬 Отзывы",
            callback_data="show_reviews"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="❓ Частые вопросы",
            callback_data="show_faq"
        ),
        InlineKeyboardButton(
            text="🌟 Истории успеха",
            callback_data="show_success_stories"
        )
    )
    
    return builder.as_markup()


def get_info_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для информационных разделов с дополнительными опциями"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📝 Записаться на курс",
            callback_data="start_application"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="💬 Почитать отзывы",
            callback_data="show_reviews"
        ),
        InlineKeyboardButton(
            text="❓ FAQ",
            callback_data="show_faq"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="↩️ В главное меню",
            callback_data="back_to_start"
        )
    )
    
    return builder.as_markup()


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отправки номера телефона"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(
            text="📱 Отправить номер телефона",
            request_contact=True
        )
    )
    builder.row(
        KeyboardButton(text="❌ Отмена")
    )
    return builder.as_markup(resize_keyboard=True)


def get_contact_time_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора времени связи"""
    builder = InlineKeyboardBuilder()
    
    for time in CONTACT_TIMES:
        builder.row(
            InlineKeyboardButton(
                text=time,
                callback_data=f"time:{time}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel_application"
        )
    )
    
    return builder.as_markup()


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура отмены"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)


def get_back_to_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура возврата к началу"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📝 Записаться на курс",
            callback_data="start_application"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="↩️ В главное меню",
            callback_data="back_to_start"
        )
    )
    
    return builder.as_markup()


def get_success_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после успешной заявки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📚 Программа курса",
            callback_data="show_program"
        ),
        InlineKeyboardButton(
            text="💬 Отзывы",
            callback_data="show_reviews"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="❓ Частые вопросы",
            callback_data="show_faq"
        ),
        InlineKeyboardButton(
            text="🌟 Истории успеха",
            callback_data="show_success_stories"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🏠 В главное меню",
            callback_data="back_to_start"
        )
    )
    
    return builder.as_markup()


def get_application_navigation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой Назад для процесса заявки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="back_to_start"
        )
    )
    
    return builder.as_markup()
