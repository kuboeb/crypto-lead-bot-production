"""
Обработчики команд для быстрого доступа к разделам
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.config import MESSAGES
from app.keyboards.user import get_info_keyboard, get_back_to_start_keyboard

router = Router(name="commands")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда помощи"""
    help_text = """
📚 <b>Доступные команды:</b>

/start - Главное меню
/help - Это сообщение
/course - Программа курса
/faq - Частые вопросы
/reviews - Отзывы выпускников
/about - О нас
/guarantees - Наши гарантии
/why_crypto - Почему криптовалюта
/success - Истории успеха

💡 <i>Используйте эти команды для быстрого доступа к нужной информации</i>
"""
    await message.answer(
        help_text,
        reply_markup=get_back_to_start_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("course"))
async def cmd_course(message: Message):
    """Программа курса"""
    await message.answer(
        MESSAGES['program'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("faq"))
async def cmd_faq(message: Message):
    """Частые вопросы"""
    await message.answer(
        MESSAGES['faq'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("reviews"))
async def cmd_reviews(message: Message):
    """Отзывы"""
    from app.database.queries import get_random_reviews
    
    reviews = await get_random_reviews(limit=3)
    
    text = "<b>💬 Отзывы наших выпускников:</b>\n\n"
    
    for review in reviews:
        text += f"<b>{review.name}</b> ({review.country})"
        if review.profit:
            text += f" - <i>{review.profit}</i>"
        text += f"\n{review.text}\n\n"
    
    text += "<i>Это лишь малая часть отзывов. Присоединяйтесь к успешным выпускникам!</i>"
    
    await message.answer(
        text,
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("about"))
async def cmd_about(message: Message):
    """О нас"""
    await message.answer(
        MESSAGES['about_us'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("guarantees"))
async def cmd_guarantees(message: Message):
    """Гарантии"""
    await message.answer(
        MESSAGES['guarantees'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("why_crypto"))
async def cmd_why_crypto(message: Message):
    """Почему криптовалюта"""
    await message.answer(
        MESSAGES['why_crypto'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("success"))
async def cmd_success(message: Message):
    """Истории успеха"""
    await message.answer(
        MESSAGES['success_stories'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("info"))
async def cmd_info(message: Message):
    """Информация о курсе"""
    await message.answer(
        MESSAGES['info'],
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )
