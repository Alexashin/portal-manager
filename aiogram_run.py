import asyncio
from create_bot import bot, dp
from db import init_db


def register_routers(dp):
    from handlers import admin_router, intern_router, employee_router, start_router

    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(intern_router)
    dp.include_router(employee_router)
    
async def main():
    register_routers(dp)
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

