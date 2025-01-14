from aiogram.filters import BaseFilter
from aiogram.types import Message
import asyncpg
from config_loader import DATABASE_URL

class RoleFilter(BaseFilter):
    def __init__(self, role: str):
        self.role = role

    async def __call__(self, message: Message) -> bool:
        query = """
        SELECT r.name FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.tg_id = $1
        """
        async with asyncpg.create_pool(DATABASE_URL) as pool:
            async with pool.acquire() as connection:
                user_role = await connection.fetchval(query, message.from_user.id)
                return user_role == self.role
