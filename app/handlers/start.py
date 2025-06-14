"""
Обработчик команды /start
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.config import MESSAGES
from app.keyboards.user import get_start_keyboard, get_back_to_start_keyboard, get_after_application_keyboard
from app.database.queries import user_has_application, get_random_reviews, get_buyer_by_code, increment_buyer_stats
from app.handlers.referral import process_referral_link

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    # Сбрасываем состояние
    await state.clear()
    
    # Проверяем, есть ли реферальная ссылка
    args = message.text.split()
    if len(args) > 1:
        # Проверяем реферальную ссылку
        if args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].split("_")[1])
            await process_referral_link(message, state, referrer_id)
        except (ValueError, IndexError):
            pass
        # Проверяем ссылку байера
        elif args[1].startswith("buyer_"):
            try:
                # Парсим параметры байера
                parts = args[1].split('_', 3)
                if len(parts) >= 3:
                    buyer_code = f"{parts[0]}_{parts[1]}_{parts[2]}"
                    
                    # Проверяем существует ли байер
                    buyer = await get_buyer_by_code(buyer_code)
                    if buyer:
                        # Увеличиваем счетчик переходов
                        await increment_buyer_stats(buyer_code)
                        
                        # Сохраняем в состоянии для последующего использования
                        await state.update_data(
                            buyer_code=buyer_code,
                            utm_params=parts[3] if len(parts) > 3 else None
                        )
            except Exception as e:
                print(f"Ошибка обработки байерской ссылки: {e}")
    
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
        await callback.answer()
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


@router.callback_query(F.data == "show_reviews")
async def show_reviews(callback: CallbackQuery):
    """Показать отзывы"""
    # Получаем 3 случайных отзыва
    reviews = await get_random_reviews(limit=3)
    
    text = "<b>💬 Отзывы наших выпускников:</b>\n\n"
    
    for review in reviews:
        text += f"<b>{review.name}</b> ({review.country})"
        if review.profit:
            text += f" - <i>{review.profit}</i>"
        text += f"\n{review.text}\n\n"
    
    text += "<i>Это лишь малая часть отзывов. Присоединяйтесь к успешным выпускникам!</i>"
    
    # Проверяем, есть ли заявка у пользователя
    has_application = await user_has_application(callback.from_user.id)
    
    if has_application:
        # Для тех, кто уже записан - показываем другую клавиатуру
        await callback.message.edit_text(
            text,
            reply_markup=get_after_application_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_start_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()
