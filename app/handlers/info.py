"""
Обработчики информационных разделов
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.config import MESSAGES
from app.keyboards.user import get_info_keyboard, get_back_to_start_keyboard, get_after_application_keyboard
from app.database.queries import user_has_application

router = Router(name="info")


async def get_keyboard_for_user(user_id: int):
    """Возвращает клавиатуру в зависимости от статуса пользователя"""
    if await user_has_application(user_id):
        return get_after_application_keyboard()
    return get_info_keyboard()


@router.callback_query(F.data == "show_faq")
async def show_faq(callback: CallbackQuery):
    """Показать FAQ"""
    keyboard = await get_keyboard_for_user(callback.from_user.id)
    await callback.message.edit_text(
        MESSAGES['faq'],
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_why_crypto")
async def show_why_crypto(callback: CallbackQuery):
    """Показать почему криптовалюта"""
    keyboard = await get_keyboard_for_user(callback.from_user.id)
    await callback.message.edit_text(
        MESSAGES['why_crypto'],
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_program")
async def show_program(callback: CallbackQuery):
    """Показать программу курса"""
    keyboard = await get_keyboard_for_user(callback.from_user.id)
    await callback.message.edit_text(
        MESSAGES['program'],
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_guarantees")
async def show_guarantees(callback: CallbackQuery):
    """Показать гарантии"""
    keyboard = await get_keyboard_for_user(callback.from_user.id)
    await callback.message.edit_text(
        MESSAGES['guarantees'],
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_about")
async def show_about(callback: CallbackQuery):
    """Показать информацию о нас"""
    keyboard = await get_keyboard_for_user(callback.from_user.id)
    await callback.message.edit_text(
        MESSAGES['about_us'],
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_success_stories")
async def show_success_stories(callback: CallbackQuery):
    """Показать истории успеха"""
    keyboard = await get_keyboard_for_user(callback.from_user.id)
    await callback.message.edit_text(
        MESSAGES['success_stories'],
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()
