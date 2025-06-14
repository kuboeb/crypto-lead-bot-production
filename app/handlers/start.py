"""
Обработчик команды /start
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards.main import get_main_keyboard
from app.database.models import async_session, User
from sqlalchemy import select

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    # Очищаем состояние
    await state.clear()
    
    # Проверяем/создаем пользователя
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            try:
                user = User(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name
                )
                session.add(user)
                await session.commit()
            except Exception as e:
                print(f"Error creating user: {e}")
    
    # Отправляем приветствие
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🎓 Добро пожаловать в бота для записи на бесплатные курсы по криптовалюте!\n\n"
        "📚 Здесь вы можете:\n"
        "• Записаться на обучение\n"
        "• Узнать о программе курса\n"
        "• Прочитать отзывы выпускников\n\n"
        "Выберите интересующий раздел:",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "🏠 Главное меню")
async def main_menu(message: types.Message, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await message.answer(
        "🏠 Вы в главном меню.\nВыберите интересующий раздел:",
        reply_markup=get_main_keyboard()
    )
