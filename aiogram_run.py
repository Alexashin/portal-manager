import asyncio
from create_bot import bot, dp
from handlers.admin_handlers import ad_router
from handlers.user_handlers import router
from db import init_db

async def main():
    dp.include_router(ad_router)
    dp.include_router(router)
    await init_db()  # Инициализация пула подключений к БД
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
