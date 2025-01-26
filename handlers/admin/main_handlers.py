from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import RoleFilter
from keyboards import *

admin_router = Router()


# Обработчик кнопки "🔙 Назад"
@admin_router.message(RoleFilter("manager"), F.text == "🔙 Назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню.", reply_markup=get_admin_keyboard()
    )


# Обработчик кнопки "📚 Управление обучением"
@admin_router.message(RoleFilter("manager"), F.text == "📚 Управление обучением")
async def manage_training(message: Message):
    await message.answer(
        "Выберите действие:", reply_markup=get_training_management_inline_keyboard()
    )


# Обработчик кнопки "👥 Пользователи"
@admin_router.message(RoleFilter("manager"), F.text == "👥 Пользователи")
async def view_users(message: Message):
    await message.answer("📋 Список пользователей будет здесь.")


# Обработчик кнопки "📊 Статистика"
@admin_router.message(RoleFilter("manager"), F.text == "📊 Статистика")
async def view_statistics(message: Message):
    await message.answer("📈 Статистика будет здесь.")
