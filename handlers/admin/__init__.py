from .module_handlers import admin_router as admin_module_router
from .lesson_handlers import admin_router as admin_lesson_router
from .test_handlers import admin_router as admin_test_router
from .user_management import admin_router as admin_user_router
from .main_handlers import admin_router as admin_main_router

__all__ = [
    "admin_main_router",
    "admin_module_router",
    "admin_lesson_router",
    "admin_test_router",
    "admin_user_router",
]
