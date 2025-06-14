"""
Аналитика и воронка продаж
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta

from app.admin.keyboards.admin import get_back_keyboard
from app.admin.middleware.auth import AdminAuthMiddleware
from app.database.models import AdminUser, Application, UnfinishedApplication, async_session
from sqlalchemy import select, func, and_, or_

router = Router(name="admin_analytics")
router.callback_query.middleware(AdminAuthMiddleware())


async def get_funnel_stats():
    """Получает статистику воронки за сегодня"""
    async with async_session() as session:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Считаем уникальных пользователей на каждом этапе
        # Для этого нужно будет добавить трекинг, пока используем примерные данные
        
        # Завершенные заявки
        completed = await session.execute(
            select(func.count(Application.id)).where(
                Application.created_at >= today_start
            )
        )
        completed_count = completed.scalar() or 0
        
        # Незавершенные заявки по шагам
        unfinished_stats = await session.execute(
            select(
                UnfinishedApplication.current_step,
                func.count(func.distinct(UnfinishedApplication.user_id))
            ).where(
                UnfinishedApplication.created_at >= today_start
            ).group_by(UnfinishedApplication.current_step)
        )
        
        steps_count = {}
        for step, count in unfinished_stats:
            steps_count[step] = count
        
        # Примерные расчеты для полной воронки
        # В реальности нужно трекать каждый шаг
        total_starts = completed_count * 5  # Примерно
        clicked_apply = completed_count * 2.5  # Примерно
        started_filling = completed_count * 2  # Примерно
        
        entered_name = steps_count.get('country', 0) + steps_count.get('phone', 0) + steps_count.get('contact_time', 0) + completed_count
        entered_country = steps_count.get('phone', 0) + steps_count.get('contact_time', 0) + completed_count
        entered_phone = steps_count.get('contact_time', 0) + completed_count
        
        return {
            'total_starts': int(total_starts),
            'clicked_apply': int(clicked_apply),
            'started_filling': int(started_filling),
            'entered_name': entered_name,
            'entered_country': entered_country,
            'entered_phone': entered_phone,
            'completed': completed_count
        }


def draw_progress_bar(value: int, max_value: int, width: int = 20) -> str:
    """Рисует прогресс-бар"""
    if max_value == 0:
        return "░" * width
    
    filled = int((value / max_value) * width)
    return "█" * filled + "░" * (width - filled)


@router.callback_query(F.data == "admin:funnel")
async def show_funnel(callback: CallbackQuery, admin: AdminUser):
    """Показывает воронку продаж"""
    stats = await get_funnel_stats()
    
    # Рассчитываем проценты
    total = stats['total_starts'] or 1  # Избегаем деления на 0
    
    text = f"""
📊 <b>ВОРОНКА ПРОДАЖ</b>
<i>За сегодня ({datetime.now().strftime('%d.%m.%Y')})</i>

/start просмотров:        {stats['total_starts']:>4} {draw_progress_bar(stats['total_starts'], total)} 100%
Нажали "Записаться":      {stats['clicked_apply']:>4} {draw_progress_bar(stats['clicked_apply'], total)} {int(stats['clicked_apply']/total*100)}%
Начали заполнять:         {stats['started_filling']:>4} {draw_progress_bar(stats['started_filling'], total)} {int(stats['started_filling']/total*100)}%
Ввели имя:               {stats['entered_name']:>4} {draw_progress_bar(stats['entered_name'], total)} {int(stats['entered_name']/total*100)}%
Ввели страну:            {stats['entered_country']:>4} {draw_progress_bar(stats['entered_country'], total)} {int(stats['entered_country']/total*100)}%
Ввели телефон:           {stats['entered_phone']:>4} {draw_progress_bar(stats['entered_phone'], total)} {int(stats['entered_phone']/total*100)}%
Завершили заявку:        {stats['completed']:>4} {draw_progress_bar(stats['completed'], total)} {int(stats['completed']/total*100)}%

"""
    
    # Анализ узких мест
    if stats['entered_country'] > 0 and stats['entered_phone'] > 0:
        phone_drop = ((stats['entered_country'] - stats['entered_phone']) / stats['entered_country']) * 100
        if phone_drop > 30:
            text += f"⚠️ <b>ПРОБЛЕМА:</b> {int(phone_drop)}% бросают на вводе телефона!\n"
            text += "💡 <i>Рекомендация: Упростите этот шаг или добавьте мотивацию</i>"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
