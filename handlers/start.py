from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from filters.role_filter import RoleFilter

rout = Router()

@rout.message(CommandStart(), RoleFilter("manager"))
async def cmd_start(message: Message):
    await message.answer('Старт менеджер')

# Хендлер для стажёра
@rout.message(CommandStart(), RoleFilter("intern"))
async def intern_start(message: Message):
    await message.answer("Добро пожаловать в раздел обучения!")

# Хендлер для сотрудника
@rout.message(CommandStart(), RoleFilter("employee"))
async def employee_start(message: Message):
    await message.answer("Вы уже прошли обучение!")