from aiogram import Router, F
from aiogram.types import Message
from filters import RoleFilter
from keyboards import get_employee_keyboard

employee_router = Router()

# Старт для сотрудника
@employee_router.message(RoleFilter("employee"), F.text == "/start")
async def employee_start(message: Message):
    await message.answer("👋 Добро пожаловать в рабочий портал!", reply_markup=get_employee_keyboard())
