from aiogram import Router
from aiogram.types import Message
from filters.role_filter import RoleFilter
from keyboards.main_keyboards import get_admin_keyboard, get_intern_keyboard, get_employee_keyboard

start_router = Router()

# Автоматический старт в зависимости от роли
@start_router.message(RoleFilter("manager"))
async def start_admin(message: Message):
    await message.answer("👋 Привет, админ!", reply_markup=get_admin_keyboard())

@start_router.message(RoleFilter("intern"))
async def start_intern(message: Message):
    await message.answer("👋 Добро пожаловать на обучение!", reply_markup=get_intern_keyboard())

@start_router.message(RoleFilter("employee"))
async def start_employee(message: Message):
    await message.answer("👋 Добро пожаловать в рабочий портал!", reply_markup=get_employee_keyboard())
