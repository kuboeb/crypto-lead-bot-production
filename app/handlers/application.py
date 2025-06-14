"""
Обработчик процесса подачи заявки
"""
import re
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
    get_cancel_keyboard, get_success_keyboard
)
from app.database.queries import create_application, user_has_application

router = Router(name="application")


@router.callback_query(F.data == "start_application")
async def start_application(callback: CallbackQuery, state: FSMContext):
    """Начало процесса заявки"""
    # Проверяем, нет ли уже заявки
    if await user_has_application(callback.from_user.id):
        await callback.message.edit_text(
            MESSAGES['already_applied'],
            parse_mode="HTML",
            reply_markup=get_success_keyboard()
        )
        await callback.answer("У вас уже есть заявка!")
        return
    
    # Запрашиваем имя
    await callback.message.edit_text(
        MESSAGES['ask_name'],
        parse_mode="HTML",
            reply_markup=get_success_keyboard()
    )
    await state.set_state(ApplicationStates.waiting_for_name)
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
            reply_markup=get_cancel_keyboard, get_success_keyboard()
        )
        return
    
    # Сохраняем имя
    await state.update_data(name=name)
    
    # Запрашиваем страну
    await message.answer(
        MESSAGES['ask_country'],
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard, get_success_keyboard()
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
            reply_markup=get_cancel_keyboard, get_success_keyboard()
        )
        return
    
    # Сохраняем страну
    await state.update_data(country=country)
    
    # Запрашиваем телефон
    await message.answer(
        MESSAGES['ask_phone'],
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
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
    
    # Запрашиваем время
    await message.answer(
        MESSAGES['ask_time'],
        parse_mode="HTML",
        reply_markup=get_contact_time_keyboard()
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
        
        # Отправляем подтверждение пользователю
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
            parse_mode="HTML",
            reply_markup=get_success_keyboard()
        )
    
    await callback.answer()


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
