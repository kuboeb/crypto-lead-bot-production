"""
Обработчик команды /start
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.config import MESSAGES
from app.keyboards.user import get_start_keyboard, get_back_to_start_keyboard, get_after_application_keyboard
from app.database.queries import user_has_application

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    # Сбрасываем состояние
    await state.clear()
    
    # Проверяем, есть ли уже заявка от пользователя
    if await user_has_application(message.from_user.id):
        await message.answer(
            MESSAGES['already_applied'],
            reply_markup=get_after_application_keyboard(),
            parse_mode="HTML"
        )
        return
    
    # Отправляем приветствие
    await message.answer(
        MESSAGES['welcome'],
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    """Возврат к началу"""
    await state.clear()
    
    # Проверяем, есть ли уже заявка
    if await user_has_application(callback.from_user.id):
        await callback.message.edit_text(
            MESSAGES['already_applied'],
            reply_markup=get_after_application_keyboard(),
            parse_mode="HTML"
        )
        return
    
    await callback.message.edit_text(
        MESSAGES['welcome'],
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "course_info")
async def show_course_info(callback: CallbackQuery):
    """Показать информацию о курсе"""
    await callback.message.edit_text(
        MESSAGES['info'],
        reply_markup=get_back_to_start_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
