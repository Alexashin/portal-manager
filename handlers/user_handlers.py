from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from filters.role_filter import RoleFilter

router = Router()

# Хендлер для стажёра
@router.message(CommandStart(), RoleFilter("intern"))
async def intern_start(message: Message) -> None:
    await message.answer("Добро пожаловать в раздел обучения!")

# Хендлер для сотрудника
@router.message(CommandStart(), RoleFilter("employee"))
async def employee_start(message: Message) -> None:
    await message.answer("Вы уже прошли обучение!")