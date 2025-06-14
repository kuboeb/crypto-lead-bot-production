"""
Система напоминаний для незавершенных заявок
"""
import asyncio
import json
from datetime import datetime
from aiogram import Bot
from app.database.queries import (
    get_unfinished_applications_for_reminder,
    mark_reminder_sent
)
from app.keyboards.user import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import BOT_TOKEN


async def send_reminder(bot: Bot, user_id: int, current_step: str, data: dict):
    """Отправить напоминание пользователю"""
    
    # Создаем персонализированное сообщение в зависимости от шага
    if current_step == "name":
        text = "🔔 <b>Вы не завершили заявку!</b>\n\n"
        text += "Остался всего один шаг до записи на бесплатный курс по криптовалюте.\n\n"
        text += "⚡ <i>Места быстро заканчиваются!</i>"
    
    elif current_step == "country":
        name = data.get('name', 'друг')
        text = f"🔔 <b>{name}, вы почти у цели!</b>\n\n"
        text += "Вы начали заполнять заявку, но не указали страну.\n"
        text += "Завершите регистрацию сейчас, пока есть места!\n\n"
        text += "💎 <i>Осталось всего 3 простых шага</i>"
    
    elif current_step == "phone":
        name = data.get('name', 'друг')
        text = f"🔔 <b>{name}, не упустите шанс!</b>\n\n"
        text += "Вы почти завершили регистрацию на курс.\n"
        text += "Осталось указать только номер телефона.\n\n"
        text += "📞 <i>Наш менеджер ждет вашу заявку</i>"
    
    elif current_step == "contact_time":
        name = data.get('name', 'друг')
        text = f"🔔 <b>{name}, последний шаг!</b>\n\n"
        text += "Вы заполнили почти всю заявку!\n"
        text += "Осталось только выбрать удобное время для звонка.\n\n"
        text += "✅ <i>Завершите регистрацию прямо сейчас!</i>"
    
    else:
        text = "🔔 <b>Завершите вашу заявку!</b>\n\n"
        text += "Вы начали регистрацию на бесплатный курс по криптовалюте.\n"
        text += "Не упустите возможность изменить свою жизнь!\n\n"
        text += "🚀 <i>Места ограничены!</i>"
    
    # Добавляем социальное доказательство
    text += "\n\n💬 <i>За последние 2 часа записалось 12 человек</i>"
    
    # Кнопка для продолжения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Продолжить заполнение",
            callback_data="continue_application"
        )
    ]])
    
    try:
        await bot.send_message(
            user_id,
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        # Отмечаем, что напоминание отправлено
        await mark_reminder_sent(user_id)
        
    except Exception as e:
        print(f"Ошибка отправки напоминания пользователю {user_id}: {e}")


async def check_and_send_reminders(bot: Bot):
    """Проверить и отправить напоминания"""
    
    # Получаем незавершенные заявки
    unfinished = await get_unfinished_applications_for_reminder()
    
    for app in unfinished:
        # Парсим данные
        data = json.loads(app.data) if app.data else {}
        
        # Отправляем напоминание
        await send_reminder(bot, app.user_id, app.current_step, data)
        
        # Небольшая задержка между отправками
        await asyncio.sleep(1)
    
    if unfinished:
        print(f"Отправлено {len(unfinished)} напоминаний")


async def reminder_task(bot: Bot):
    """Фоновая задача для проверки напоминаний"""
    while True:
        try:
            await check_and_send_reminders(bot)
        except Exception as e:
            print(f"Ошибка в задаче напоминаний: {e}")
        
        # Проверяем каждые 5 минут
        await asyncio.sleep(300)
