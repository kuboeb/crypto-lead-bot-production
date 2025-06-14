"""
Обработчик процесса подачи заявки
"""
import re
import json
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from app.config import MESSAGES, ADMIN_ID
from app.states.application import ApplicationStates
from app.keyboards.user import (
    get_phone_keyboard, 
    get_contact_time_keyboard,
    get_cancel_keyboard,
    get_success_keyboard
)
from app.database.queries import (
    create_application, 
    user_has_application,
    save_unfinished_application,
    get_recent_applications_count,
    get_recent_applications
)

router = Router(name="application")


def get_progress_bar(current_step: int, total_steps: int = 4) -> str:
    """Генерирует прогресс-бар"""
    filled = "▓" * current_step
    empty = "░" * (total_steps - current_step)
    percentage = (current_step / total_steps) * 100
    return f"{filled}{empty} {percentage:.0f}%"


def get_social_proof() -> str:
    """Генерирует социальное доказательство"""
    import random
    messages = [
        "💫 За последний час записалось 7 человек",
        "🔥 Осталось 12 мест в группе",
        "⚡ Михаил из Германии только что записался",
        "🎯 Уже 89 человек проходят обучение",
        "✨ Анна из Франции начала зарабатывать 1500€/мес"
    ]
    return random.choice(messages)


@router.callback_query(F.data == "start_application")
async def start_application(callback: CallbackQuery, state: FSMContext):
    """Начало процесса заявки"""
    # Проверяем, нет ли уже заявки
    if await user_has_application(callback.from_user.id):
        await callback.message.edit_text(
            MESSAGES['already_applied'],
            parse_mode="HTML"
        )
        await callback.answer("У вас уже есть заявка!")
        return
    
    # Добавляем социальное доказательство
    social_proof = get_social_proof()
    progress = get_progress_bar(1)
    
    # Запрашиваем имя
    text = f"<b>Шаг 1 из 4</b> {progress}\n\n"
    text += MESSAGES['ask_name']
    text += f"\n\n<i>{social_proof}</i>"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(ApplicationStates.waiting_for_name)
    
    # Сохраняем начало заполнения
    await save_unfinished_application(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        current_step="name",
        data={}
    )
    
    await callback.answer()


@router.message(ApplicationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка имени"""
    name = message.text.strip()
    
    # Проверяем, что имя содержит только буквы и пробелы
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s]+$', name):
        await message.answer(
            MESSAGES['invalid_name'],
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Сохраняем имя
    await state.update_data(name=name)
    
    # Обновляем прогресс
    progress = get_progress_bar(2)
    
    # Персонализированное обращение
    text = f"<b>Шаг 2 из 4</b> {progress}\n\n"
    text += f"Отлично, {name}! "
    text += MESSAGES['ask_country']
    
    # Показываем недавние заявки
    recent_count = await get_recent_applications_count(hours=1)
    if recent_count > 0:
        text += f"\n\n<i>💡 За последний час к нам присоединилось {recent_count} человек(а)</i>"
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    
    # Сохраняем прогресс
    data = await state.get_data()
    await save_unfinished_application(
        user_id=message.from_user.id,
        username=message.from_user.username,
        current_step="country",
        data=data
    )
    
    await state.set_state(ApplicationStates.waiting_for_country)


@router.message(ApplicationStates.waiting_for_country)
async def process_country(message: Message, state: FSMContext):
    """Обработка страны"""
    country = message.text.strip()
    
    # Базовая проверка
    if len(country) < 2 or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s\-]+$', country):
        await message.answer(
            MESSAGES['invalid_country'],
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Сохраняем страну
    await state.update_data(country=country)
    data = await state.get_data()
    
    # Обновляем прогресс
    progress = get_progress_bar(3)
    
    text = f"<b>Шаг 3 из 4</b> {progress}\n\n"
    text += f"Супер, {data['name']}! "
    text += MESSAGES['ask_phone']
    
    # Показываем последнюю заявку из этой страны
    recent_apps = await get_recent_applications(limit=10)
    for app in recent_apps:
        if app.country.lower() == country.lower():
            text += f"\n\n<i>🌍 Кстати, из {country} недавно записался {app.name}</i>"
            break
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )
    
    # Сохраняем прогресс
    await save_unfinished_application(
        user_id=message.from_user.id,
        username=message.from_user.username,
        current_step="phone",
        data=data
    )
    
    await state.set_state(ApplicationStates.waiting_for_phone)


@router.message(ApplicationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка номера телефона"""
    phone = None
    
    # Если пользователь поделился контактом
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith('+'):
            phone = '+' + phone
    else:
        # Если ввел вручную
        phone = message.text.strip()
        # Проверяем формат
        if not re.match(r'^\+\d{10,15}$', phone):
            await message.answer(
                MESSAGES['invalid_phone'],
                parse_mode="HTML",
                reply_markup=get_phone_keyboard()
            )
            return
    
    # Сохраняем телефон
    await state.update_data(phone=phone)
    data = await state.get_data()
    
    # Обновляем прогресс
    progress = get_progress_bar(4)
    
    text = f"<b>Последний шаг!</b> {progress}\n\n"
    text += f"Отлично, {data['name']}! "
    text += MESSAGES['ask_time']
    text += "\n\n<i>🎯 После выбора времени ваше место будет забронировано!</i>"
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_contact_time_keyboard()
    )
    
    # Сохраняем прогресс
    await save_unfinished_application(
        user_id=message.from_user.id,
        username=message.from_user.username,
        current_step="contact_time",
        data=data
    )
    
    await state.set_state(ApplicationStates.waiting_for_contact_time)


@router.callback_query(ApplicationStates.waiting_for_contact_time, F.data.startswith("time:"))
async def process_contact_time(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Обработка времени связи"""
    # Получаем время из callback data
    contact_time = callback.data.split(":", 1)[1]
    
    # Получаем все данные
    data = await state.get_data()
    
    try:
        # Создаём заявку в БД
        application = await create_application(
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            name=data['name'],
            country=data['country'],
            phone=data['phone'],
            contact_time=contact_time
        )
        
        # Отправляем подтверждение пользователю с клавиатурой
        await callback.message.edit_text(
            MESSAGES['success'],
            parse_mode="HTML",
            reply_markup=get_success_keyboard()
        )
        
        # Отправляем уведомление админу
        admin_text = MESSAGES['admin_notification'].format(
            name=data['name'],
            country=data['country'],
            phone=data['phone'],
            contact_time=contact_time,
            created_at=application.created_at.strftime("%d.%m.%Y %H:%M"),
            user_id=callback.from_user.id
        )
        
        try:
            await bot.send_message(
                ADMIN_ID,
                admin_text,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Ошибка отправки админу: {e}")
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        print(f"Ошибка создания заявки: {e}")
        await callback.message.edit_text(
            MESSAGES['error'],
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data == "continue_application")
async def continue_application(callback: CallbackQuery, state: FSMContext):
    """Продолжить заполнение заявки после напоминания"""
    # Получаем незавершенную заявку из БД
    from app.database.models import async_session, UnfinishedApplication
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(UnfinishedApplication).where(
                UnfinishedApplication.user_id == callback.from_user.id
            )
        )
        unfinished = result.scalar_one_or_none()
    
    if not unfinished:
        await callback.message.edit_text(
            "Начните заново, нажав /start",
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Восстанавливаем данные
    data = json.loads(unfinished.data) if unfinished.data else {}
    await state.update_data(**data)
    
    # Определяем, на каком шаге остановился пользователь
    if unfinished.current_step == "name":
        progress = get_progress_bar(1)
        text = f"<b>Шаг 1 из 4</b> {progress}\n\n"
        text += MESSAGES['ask_name']
        await callback.message.edit_text(text, parse_mode="HTML")
        await state.set_state(ApplicationStates.waiting_for_name)
        
    elif unfinished.current_step == "country":
        progress = get_progress_bar(2)
        text = f"<b>Шаг 2 из 4</b> {progress}\n\n"
        text += f"С возвращением, {data.get('name', '')}! "
        text += MESSAGES['ask_country']
        await callback.message.edit_text(text, parse_mode="HTML")
        await state.set_state(ApplicationStates.waiting_for_country)
        
    elif unfinished.current_step == "phone":
        progress = get_progress_bar(3)
        text = f"<b>Шаг 3 из 4</b> {progress}\n\n"
        text += f"Продолжаем, {data.get('name', '')}! "
        text += MESSAGES['ask_phone']
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_phone_keyboard()
        )
        await callback.message.delete()
        await state.set_state(ApplicationStates.waiting_for_phone)
        
    elif unfinished.current_step == "contact_time":
        progress = get_progress_bar(4)
        text = f"<b>Последний шаг!</b> {progress}\n\n"
        text += f"Почти готово, {data.get('name', '')}! "
        text += MESSAGES['ask_time']
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_contact_time_keyboard()
        )
        await callback.message.delete()
        await state.set_state(ApplicationStates.waiting_for_contact_time)
    
    await callback.answer("Продолжаем с того места, где остановились!")


@router.message(F.text == "❌ Отмена")
@router.callback_query(F.data == "cancel_application")
async def cancel_application(update: Message | CallbackQuery, state: FSMContext):
    """Отмена заявки"""
    await state.clear()
    
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(
            MESSAGES['cancelled'],
            parse_mode="HTML"
        )
        await update.answer()
    else:
        await update.answer(
            MESSAGES['cancelled'],
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )
