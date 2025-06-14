"""
Главное меню админ-панели
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.admin.keyboards.admin import get_admin_main_keyboard
from app.admin.middleware.auth import AdminAuthMiddleware
from app.database.models import AdminUser

router = Router(name="admin_main")

# Применяем middleware ко всем обработчикам в этом роутере
router.message.middleware(AdminAuthMiddleware())
router.callback_query.middleware(AdminAuthMiddleware())


@router.message(Command("admin"))
async def cmd_admin(message: Message, admin: AdminUser):
    """Вход в админ-панель"""
    await message.answer(
        f"👨‍💼 <b>Админ-панель</b>\n\n"
        f"Добро пожаловать, {admin.full_name or admin.username}!\n"
        f"Ваша роль: <b>{admin.role}</b>\n\n"
        f"Выберите раздел:",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin:main")
async def admin_main_menu(callback: CallbackQuery, admin: AdminUser):
    """Возврат в главное меню админки"""
    await callback.message.edit_text(
        f"👨‍💼 <b>Админ-панель</b>\n\n"
        f"Добро пожаловать, {admin.full_name or admin.username}!\n"
        f"Ваша роль: <b>{admin.role}</b>\n\n"
        f"Выберите раздел:",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
