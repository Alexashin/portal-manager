from aiogram.filters import BaseFilter
from aiogram.types import Message
from db.db_controller import get_user_role  # Импорт функции из контроллера

class RoleFilter(BaseFilter):
    def __init__(self, role: str):
        self.role = role

    async def __call__(self, message: Message) -> bool:
        user_role = await get_user_role(message.from_user.id)
        return user_role == self.role
