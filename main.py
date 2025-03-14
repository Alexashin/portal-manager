import os
import asyncio
import logging
from logging import Logger
from config_loader import LOGGER_LVL
from aiogram_run import start_bot
from db import init_db


async def init_logger() -> Logger:
    # Создание папки для логов (если её нет)
    os.makedirs("logs", exist_ok=True)

    # Кастомный формат логирования
    LOG_FORMAT = "[%(levelname)s] %(asctime)s | %(name)s | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"  # Убираем миллисекунды

    # Настройка логгера
    logging.basicConfig(
        level=LOGGER_LVL,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.FileHandler("logs/bot.log", encoding="utf-8"),  # Логирование в файл
            logging.StreamHandler(),  # Логирование в консоль
        ],
    )

    logger = logging.getLogger(__name__)  # Создание папки для логов (если её нет)
    logger.info("Начата запись журнала логов")
    os.makedirs("logs", exist_ok=True)

    return logger


async def main() -> None:
    logger = await init_logger()
    try:
        await init_db()
    except Exception as ex:
        logger.error("Проверьте Docker!")
        logger.error(ex)
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
