"""
Клавиатуры для пользователей
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.config import CONTACT_TIMES


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для начала"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📝 Записаться на курс",
            callback_data="start_application"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📚 Подробнее о курсе",
            callback_data="course_info"
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
            text="↩️ Вернуться в начало",
            callback_data="back_to_start"
        )
    )
    return builder.as_markup()
