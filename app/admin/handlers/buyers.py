"""
Управление байерами (рекламщиками)
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import secrets
import string
from datetime import datetime

from app.admin.keyboards.admin import (
    get_buyers_keyboard, 
    get_buyer_sources_keyboard,
    get_back_keyboard
)
from app.admin.middleware.auth import AdminAuthMiddleware, check_admin_role
from app.database.models import AdminUser, Buyer, async_session, Application
from sqlalchemy import select, func, desc

router = Router(name="admin_buyers")
router.callback_query.middleware(AdminAuthMiddleware())
router.message.middleware(AdminAuthMiddleware())


class AddBuyerStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_telegram = State()
    choosing_source = State()
    waiting_for_pixel_data = State()


def generate_buyer_code(name: str) -> str:
    """Генерирует уникальный код для байера"""
    # Берем первые буквы имени и добавляем случайные символы
    prefix = ''.join(name.split()[:2]).lower()[:6]
    random_part = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    return f"buyer_{prefix}_{random_part}"


@router.callback_query(F.data == "admin:buyers")
async def show_buyers_menu(callback: CallbackQuery, admin: AdminUser):
    """Показывает меню управления байерами"""
    async with async_session() as session:
        # Получаем количество активных байеров
        buyers_count = await session.execute(
            select(func.count(Buyer.id)).where(Buyer.is_active == True)
        )
        count = buyers_count.scalar() or 0
        
        # Получаем топ-3 байеров по заявкам за сегодня
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        top_buyers = await session.execute(
            select(
                Buyer.name,
                func.count(Application.id).label('leads_count')
            ).join(
                Application,
                Application.referred_by == Buyer.buyer_code
            ).where(
                Application.created_at >= today_start
            ).group_by(
                Buyer.id
            ).order_by(
                desc('leads_count')
            ).limit(3)
        )
        
        top_text = ""
        for buyer_name, leads in top_buyers:
            top_text += f"• {buyer_name}: {leads} заявок\n"
        
        if not top_text:
            top_text = "Пока нет данных за сегодня"
    
    text = f"""
👥 <b>УПРАВЛЕНИЕ БАЙЕРАМИ</b>

📊 Активных байеров: {count}

<b>Топ за сегодня:</b>
{top_text}

Выберите действие:
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_buyers_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:add_buyer")
@check_admin_role("admin")
async def start_add_buyer(callback: CallbackQuery, state: FSMContext, admin: AdminUser):
    """Начинает процесс добавления байера"""
    await callback.message.edit_text(
        "➕ <b>Добавление нового байера</b>\n\n"
        "Введите имя байера (например: Александр или Team Alpha):",
        parse_mode="HTML"
    )
    await state.set_state(AddBuyerStates.waiting_for_name)
    await callback.answer()


@router.message(AddBuyerStates.waiting_for_name)
async def process_buyer_name(message: Message, state: FSMContext, admin: AdminUser):
    """Обрабатывает имя байера"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Попробуйте еще раз:")
        return
    
    await state.update_data(name=name)
    
    await message.answer(
        f"Имя: <b>{name}</b>\n\n"
        "Теперь введите Telegram username байера (без @) или пропустите этот шаг, отправив -",
        parse_mode="HTML"
    )
    await state.set_state(AddBuyerStates.waiting_for_telegram)


@router.message(AddBuyerStates.waiting_for_telegram)
async def process_buyer_telegram(message: Message, state: FSMContext, admin: AdminUser):
    """Обрабатывает telegram байера"""
    telegram = message.text.strip()
    
    if telegram != "-":
        # Убираем @ если есть
        telegram = telegram.replace("@", "")
        await state.update_data(telegram_username=telegram)
    
    await message.answer(
        "Выберите источник трафика байера:",
        reply_markup=get_buyer_sources_keyboard()
    )
    await state.set_state(AddBuyerStates.choosing_source)


@router.callback_query(AddBuyerStates.choosing_source, F.data.startswith("admin:buyer_source:"))
async def process_buyer_source(callback: CallbackQuery, state: FSMContext, admin: AdminUser):
    """Обрабатывает выбор источника трафика"""
    source = callback.data.split(":")[-1]
    await state.update_data(source_type=source)
    
    # Генерируем код байера
    data = await state.get_data()
    buyer_code = generate_buyer_code(data['name'])
    await state.update_data(buyer_code=buyer_code)
    
    # В зависимости от источника показываем разные инструкции
    if source == "facebook":
        text = f"""
✅ <b>Facebook выбран</b>

Сгенерирована ссылка для байера:
<code>https://t.me/{callback.bot.username}?start={buyer_code}_{{{{fbclid}}}}</code>

Теперь попросите байера прислать:
1. Facebook Pixel ID
2. Access Token для Conversions API

Отправьте эти данные в формате:
<code>PIXEL_ID
ACCESS_TOKEN</code>

Или отправьте - чтобы настроить позже
"""
    elif source == "google":
        text = f"""
✅ <b>Google Ads выбран</b>

Сгенерирована ссылка для байера:
<code>https://t.me/{callback.bot.username}?start={buyer_code}_{{{{gclid}}}}</code>

⚠️ ВАЖНО: gclid обязателен для отслеживания!

Отправьте - чтобы продолжить
"""
    elif source in ["propeller", "richads", "evadav", "pushhouse", "onclick"]:
        text = f"""
✅ <b>{source.title()} выбран</b>

Сгенерирована ссылка для байера:
<code>https://t.me/{callback.bot.username}?start={buyer_code}_{{{{clickid}}}}</code>

Postback URL для байера:
<code>https://yourdomain.com/postback/{source}?buyer={buyer_code}&status=lead&payout=50</code>

Отправьте - чтобы завершить настройку
"""
    else:
        text = f"""
✅ <b>Источник: {source}</b>

Сгенерирована ссылка для байера:
<code>https://t.me/{callback.bot.username}?start={buyer_code}_{{{{subid}}}}</code>

Отправьте URL для postback или - чтобы пропустить:
"""
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(AddBuyerStates.waiting_for_pixel_data)
    await callback.answer()


@router.message(AddBuyerStates.waiting_for_pixel_data)
async def process_pixel_data(message: Message, state: FSMContext, admin: AdminUser):
    """Обрабатывает данные пикселя/postback"""
    data = await state.get_data()
    
    pixel_info = {}
    if message.text.strip() != "-":
        if data['source_type'] == 'facebook':
            lines = message.text.strip().split('\n')
            if len(lines) >= 2:
                pixel_info['fb_pixel_id'] = lines[0].strip()
                pixel_info['fb_access_token'] = lines[1].strip()
        else:
            pixel_info['postback_url'] = message.text.strip()
    
    # Создаем байера в БД
    async with async_session() as session:
        buyer = Buyer(
            name=data['name'],
            telegram_username=data.get('telegram_username'),
            source_type=data['source_type'],
            buyer_code=data['buyer_code'],
            **pixel_info
        )
        session.add(buyer)
        await session.commit()
    
    # Формируем итоговое сообщение
    final_text = f"""
✅ <b>Байер успешно добавлен!</b>

<b>Информация для байера {data['name']}:</b>

📎 Ссылка для рекламы:
<code>https://t.me/{message.bot.username}?start={data['buyer_code']}</code>

📊 Источник: {data['source_type']}
"""
    
    if data['source_type'] in ["propeller", "richads", "evadav", "pushhouse", "onclick"]:
        final_text += f"""
🔗 Postback URL:
<code>https://yourdomain.com/postback/{data['source_type']}?buyer={data['buyer_code']}&status=lead&payout=50</code>
"""
    
    final_text += "\n💡 Отправьте эту информацию байеру!"
    
    await message.answer(
        final_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()


@router.callback_query(F.data == "admin:buyers_stats")
async def show_buyers_stats(callback: CallbackQuery, admin: AdminUser):
    """Показывает статистику по всем байерам"""
    async with async_session() as session:
        # Получаем статистику по байерам
        buyers_stats = await session.execute(
            select(
                Buyer.name,
                Buyer.source_type,
                Buyer.total_leads,
                Buyer.is_active,
                func.count(Application.id).label('today_leads')
            ).outerjoin(
                Application,
                (Application.referred_by == Buyer.buyer_code) & 
                (Application.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
            ).group_by(
                Buyer.id
            ).order_by(
                desc('today_leads')
            )
        )
        
        text = "📊 <b>СТАТИСТИКА БАЙЕРОВ</b>\n\n"
        
        for name, source, total, is_active, today in buyers_stats:
            status = "🟢" if is_active else "🔴"
            text += f"{status} <b>{name}</b> ({source})\n"
            text += f"├─ Сегодня: {today} заявок\n"
            text += f"└─ Всего: {total} заявок\n\n"
        
        if not text.endswith("\n\n"):
            text = "📊 <b>СТАТИСТИКА БАЙЕРОВ</b>\n\nПока нет добавленных байеров."
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
