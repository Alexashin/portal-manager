import db
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from contexts import EmployeeFSM
from keyboards import (
    get_user_role_selector_keyboard,
    get_user_managment_keyboard,
    get_user_role_managment_keyboard,
)

admin_router = Router()

log = logging.getLogger(__name__)


# Добавление сотрудника
@admin_router.callback_query(F.data == "add_user")
async def request_employee_identifier(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EmployeeFSM.waiting_for_identifier)
    await callback.message.answer(
        "📌 Отправьте Telegram ID пользователя. Для получения этого кода, ему требуется начать диалог с ботом."
    )
    await callback.answer()


# Ввод tg_id нового пользователя
@admin_router.message(EmployeeFSM.waiting_for_identifier)
async def get_employee_identifier(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("❗ Некорректный Telegram ID. Попробуйте ещё раз.")
        return

    await state.update_data(user_id=user_id)
    await state.set_state(EmployeeFSM.waiting_for_full_name)
    await message.answer("📌 Введите ФИО нового сотрудника.")


# Выбор роли нового сотрудника
@admin_router.message(EmployeeFSM.waiting_for_full_name)
async def get_employee_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(EmployeeFSM.waiting_for_role)
    await message.answer(
        "📌 Выберите роль нового сотрудника:",
        reply_markup=get_user_role_selector_keyboard(),
    )


# Добавление сотрудника в БД
@admin_router.callback_query(
    EmployeeFSM.waiting_for_role, F.data.startswith("set_role_")
)
async def set_employee_role(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split("_")[-1]  # Получаем роль (intern, employee, manager)
    role_name = {"intern": "Стажёр", "employee": "Сотрудник", "manager": "Менеджер"}[
        role
    ]

    data = await state.get_data()
    user_id = data.get("user_id")
    full_name = data.get("full_name")

    await db.add_employee(user_id, full_name, role)
    await callback.message.answer(
        f"✅ Пользователь {full_name} ({user_id}) добавлен в систему как {role_name}."
    )
    log.info(
        f"Пользователь {full_name} ({user_id}) добавлен в систему как {role_name}, менеджер {callback.from_user.id}"
    )
    await state.clear()


# Просмотр информации о сотруднике
@admin_router.callback_query(F.data.startswith("view_user_"))
async def view_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    user_info = await db.get_employee_info(user_id)

    if not user_info:
        await callback.message.answer("❗ Данный сотрудник не найден.")
        return

    response = "📌 <b>Информация о сотруднике:</b>\n"
    response += f"👤 Имя: {user_info['full_name']}\n"
    response += f"🆔 Telegram ID: {user_id}\n"
    response += f"📅 Дата регистрации: {user_info['created_at']}\n"

    await callback.message.answer(
        response, reply_markup=get_user_managment_keyboard(user_id)
    )


# Изменение роли сотрудника
@admin_router.callback_query(F.data.startswith("change_role_"))
async def change_role(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await callback.message.answer(
        "🔄 Выберите новую роль для пользователя:",
        reply_markup=get_user_role_managment_keyboard(user_id),
    )


# Обработчики смены роли
@admin_router.callback_query(F.data.startswith("set_role_"))
async def set_role(callback: CallbackQuery):
    parts = callback.data.split("_")
    role = parts[2]
    user_id = int(parts[3])

    role_name = {"intern": "Стажёр", "employee": "Сотрудник", "manager": "Менеджер"}[
        role
    ]

    await db.update_user_role(user_id, role)
    user_info = await db.get_employee_info(user_id)
    log.info(
        f"Менеджер {callback.from_user.id} изменил роль {user_info['full_name']} на {role_name}."
    )
    await callback.message.answer(
        f"✅ Пользователь {user_info['full_name']} теперь {role_name}."
    )


# Удаление сотрудника
@admin_router.callback_query(F.data.startswith("delete_employee_"))
async def delete_employee(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await db.delete_employee(user_id)
    user_info = await db.get_employee_info(user_id)
    await callback.message.answer(
        f"🗑 Сотрудник {user_info['full_name']} удалён из системы."
    )
