"""
Обработчики информационных разделов
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.config import MESSAGES
from app.keyboards.user import get_info_keyboard, get_back_to_start_keyboard

router = Router(name="info")


@router.callback_query(F.data == "show_faq")
async def show_faq(callback: CallbackQuery):
    """Показать FAQ"""
    await callback.message.edit_text(
        MESSAGES['faq'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_why_crypto")
async def show_why_crypto(callback: CallbackQuery):
    """Показать почему криптовалюта"""
    await callback.message.edit_text(
        MESSAGES['why_crypto'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_program")
async def show_program(callback: CallbackQuery):
    """Показать программу курса"""
    await callback.message.edit_text(
        MESSAGES['program'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_guarantees")
async def show_guarantees(callback: CallbackQuery):
    """Показать гарантии"""
    await callback.message.edit_text(
        MESSAGES['guarantees'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_about")
async def show_about(callback: CallbackQuery):
    """Показать информацию о нас"""
    await callback.message.edit_text(
        MESSAGES['about_us'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_success_stories")
async def show_success_stories(callback: CallbackQuery):
    """Показать истории успеха"""
    await callback.message.edit_text(
        MESSAGES['success_stories'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
