from create_bot import bot, dp

def register_routers(dp):
    from handlers import admin_router, intern_router, employee_router, start_router

    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(intern_router)
    dp.include_router(employee_router)

async def start_bot():
    register_routers(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

