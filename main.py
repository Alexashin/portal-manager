import asyncio
import logging
from aiogram_run import start_bot
from db import init_db

log = logging.getLogger(__name__)


async def main() -> None:
    log.debug("Инициализация бота")
    try:
        await init_db()
    except Exception as ex:
        log.error("Проверьте Docker!")
        log.error(ex)
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
