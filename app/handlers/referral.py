"""
Обработчик реферальной системы
"""
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.config import MESSAGES
from app.database.queries import (
    user_has_application, 
    get_user_referrals_count,
    save_referral,
    get_application_by_user_id
)

router = Router(name="referral")


def generate_referral_link(user_id: int, bot_username: str) -> str:
    """Генерирует реферальную ссылку"""
    return f"https://t.me/{bot_username}?start=ref_{user_id}"


def get_share_keyboard(referral_link: str, share_text: str) -> InlineKeyboardMarkup:
    """Клавиатура для шеринга"""
    builder = InlineKeyboardBuilder()
    
    # Кнопка поделиться в Telegram
    builder.row(
        InlineKeyboardButton(
            text="📤 Поделиться в Telegram",
            url=f"https://t.me/share/url?url={referral_link}&text={share_text}"
        )
    )
    
    # Кнопка поделиться в WhatsApp
    builder.row(
        InlineKeyboardButton(
            text="💚 Поделиться в WhatsApp",
            url=f"https://wa.me/?text={share_text} {referral_link}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="back_to_start"
        )
    )
    
    return builder.as_markup()


@router.callback_query(F.data == "show_referral_program")
async def show_referral_program(callback: CallbackQuery, bot: Bot):
    """Показать реферальную программу"""
    # Проверяем, есть ли у пользователя заявка
    if not await user_has_application(callback.from_user.id):
        await callback.answer("Сначала нужно записаться на курс!", show_alert=True)
        return
    
    # Получаем информацию о боте
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    
    # Генерируем реферальную ссылку
    referral_link = generate_referral_link(callback.from_user.id, bot_username)
    
    # Получаем количество приглашенных
    referrals_count = await get_user_referrals_count(callback.from_user.id)
    
    # Формируем текст
    text = MESSAGES['referral_program'].format(referral_link=referral_link)
    if referrals_count > 0:
        text += f"\n\n👥 <b>Вы уже пригласили: {referrals_count} чел.</b>"
        text += f"\n💰 <b>Потенциальный бонус: {referrals_count * 50}€</b>"
    
    # Текст для шеринга (URL encoded)
    share_text = MESSAGES['referral_share_message'].format(referral_link=referral_link)
    import urllib.parse
    share_text_encoded = urllib.parse.quote(share_text)
    
    await callback.message.edit_text(
        text,
        reply_markup=get_share_keyboard(referral_link, share_text_encoded),
        parse_mode="HTML"
    )
    await callback.answer()


async def process_referral_link(message: Message, state: FSMContext, referrer_id: int):
    """Обработка реферальной ссылки"""
    try:
        # Проверяем, что это не сам пользователь
        if referrer_id == message.from_user.id:
            return
        
        # Проверяем, есть ли у реферера заявка
        referrer_app = await get_application_by_user_id(referrer_id)
        if referrer_app:
            # Отправляем специальное приветствие
            welcome_text = MESSAGES['referred_welcome'].format(
                referrer_name=referrer_app.name
            )
            await message.answer(welcome_text, parse_mode="HTML")
            
            # Сохраняем информацию о реферале в состоянии
            await state.update_data(referred_by=referrer_id)
    except Exception as e:
        print(f"Ошибка обработки реферальной ссылки: {e}")
