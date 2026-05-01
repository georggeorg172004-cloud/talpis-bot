import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from ai_handler import ask_ai
from scheduler import add_subscriber, remove_subscriber

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    add_subscriber(message.from_user.id)
    await message.answer(
        "👋 Привет! Я бот календаря мероприятий <b>Talpis</b>.\n\n"
        "Я буду присылать уведомления об изменениях в расписании.\n\n"
        "Также можешь спросить меня о любом мероприятии — например:\n"
        "• <i>Когда ближайшая МВС?</i>\n"
        "• <i>Что запланировано на май?</i>\n"
        "• <i>Когда следующий вебинар?</i>",
        parse_mode="HTML",
    )


@router.message(Command("stop"))
async def cmd_stop(message: Message):
    remove_subscriber(message.from_user.id)
    await message.answer("Ты отписался от уведомлений. Напиши /start чтобы подписаться снова.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>Команды:</b>\n"
        "/start — подписаться на уведомления\n"
        "/stop — отписаться\n"
        "/help — помощь\n\n"
        "Или просто задай любой вопрос о расписании.",
        parse_mode="HTML",
    )


@router.message(F.text)
async def handle_question(message: Message):
    # В группе реагируем только на упоминание бота
    if message.chat.type in ("group", "supergroup"):
        bot_username = (await message.bot.get_me()).username
        if f"@{bot_username}" not in (message.text or ""):
            return

    await message.bot.send_chat_action(message.chat.id, "typing")

    # Убираем упоминание бота из вопроса если есть
    question = message.text or ""
    if message.chat.type in ("group", "supergroup"):
        bot_username = (await message.bot.get_me()).username
        question = question.replace(f"@{bot_username}", "").strip()

    if not question:
        return

    answer = await ask_ai(question)
    await message.answer(answer, parse_mode="HTML")
