import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from handlers import router
from scheduler import check_for_changes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        check_for_changes,
        "interval",
        minutes=config.CHECK_INTERVAL_MINUTES,
        args=[bot],
        id="check_changes",
    )
    scheduler.start()
    logger.info(f"Scheduler started, interval: {config.CHECK_INTERVAL_MINUTES} min")

    logger.info("Bot started")
    await dp.start_polling(bot, allowed_updates=["message"])


if __name__ == "__main__":
    asyncio.run(main())
