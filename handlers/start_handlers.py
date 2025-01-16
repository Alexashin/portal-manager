from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from filters import RoleFilter
from aiogram.fsm.context import FSMContext
from keyboards import get_intern_keyboard, get_employee_keyboard, get_admin_keyboard

start_router = Router()

# Автоматический старт в зависимости от роли
@start_router.message(RoleFilter("manager"), Command("start"))
async def start_admin(message: Message, state: FSMContext):
    await message.answer("👋 Привет, админ!", reply_markup=get_admin_keyboard())
    await state.clear()

@start_router.message(RoleFilter("intern"), Command("start"))
async def start_intern(message: Message, state: FSMContext):
    await message.answer("👋 Добро пожаловать на обучение!", reply_markup=get_intern_keyboard())
    await state.clear()

@start_router.message(RoleFilter("employee"), Command("start"))
async def start_employee(message: Message, state: FSMContext):
    await message.answer("👋 Добро пожаловать в рабочий портал!", reply_markup=get_employee_keyboard())
    await state.clear()
