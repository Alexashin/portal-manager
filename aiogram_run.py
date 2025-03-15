from aiogram import Dispatcher
from create_bot import bot, dp
from handlers.admin import (
    admin_module_router,
    admin_lesson_router,
    admin_test_router,
    admin_user_router,
    admin_main_router,
    admin_exam_router,
)


def register_routers(dp: Dispatcher) -> None:
    from handlers import intern_router, employee_router, start_router

    dp.include_router(start_router)
    # Роутеры админа
    dp.include_router(admin_module_router)
    dp.include_router(admin_lesson_router)
    dp.include_router(admin_test_router)
    dp.include_router(admin_user_router)
    dp.include_router(admin_main_router)
    dp.include_router(admin_exam_router)

    # Роутеры стажёра
    dp.include_router(intern_router)

    # Роутеры работника
    dp.include_router(employee_router)


async def start_bot() -> None:
    register_routers(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
