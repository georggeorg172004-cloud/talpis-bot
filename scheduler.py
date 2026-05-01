import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

import config
from comparator import compare, format_change_message, load_snapshot, save_snapshot
from sheets import fetch_events

logger = logging.getLogger(__name__)

# Хранит подписчиков которые написали боту в личку
# В продакшне лучше хранить в файле/БД, но для старта хватит памяти
_subscribers: set[int] = set()


def add_subscriber(user_id: int):
    _subscribers.add(user_id)


def remove_subscriber(user_id: int):
    _subscribers.discard(user_id)


def get_subscribers() -> set[int]:
    return _subscribers.copy()


async def send_to_all(bot: Bot, text: str):
    """Отправляет в группу и всем личным подписчикам."""
    targets = []

    if config.GROUP_CHAT_ID != 0:
        targets.append(config.GROUP_CHAT_ID)

    targets.extend(_subscribers)

    for chat_id in targets:
        try:
            await bot.send_message(chat_id, text, parse_mode="HTML")
        except TelegramBadRequest as e:
            logger.warning(f"Failed to send to {chat_id}: {e}")


async def check_for_changes(bot: Bot):
    """Основная задача планировщика."""
    logger.info("Checking for changes...")
    try:
        events = await fetch_events()
    except Exception as e:
        logger.error(f"Failed to fetch events: {e}")
        return

    old_snapshot = load_snapshot()

    if old_snapshot is None:
        # Первый запуск — просто сохраняем снимок без уведомлений
        save_snapshot(events)
        logger.info("First run — snapshot saved, no notifications sent")
        return

    changes = compare(old_snapshot, events)

    if not changes:
        logger.info("No changes detected")
        save_snapshot(events)
        return

    logger.info(f"Detected {len(changes)} changes")

    for change in changes:
        msg = format_change_message(change)
        if msg:
            await send_to_all(bot, msg)

    save_snapshot(events)
