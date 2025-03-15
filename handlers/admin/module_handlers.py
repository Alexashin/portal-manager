import db
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from filters import RoleFilter
from contexts import ModuleCreationFSM, ModuleEditFSM, TestCreationFSM
from keyboards import (
    get_modules_admin_keyboard,
    get_module_management_keyboard,
    get_back_keyboard,
    get_admin_keyboard,
    get_dangerous_accept_keyboard,
)
from handlers.admin.main_handlers import is_back

admin_router = Router()


# Показ списка модулей
@admin_router.callback_query(RoleFilter("manager"), F.data == "list_modules")
async def show_modules(callback: CallbackQuery):
    modules = await db.get_all_modules()
    if not modules:
        await callback.message.answer("❗ Модули пока не созданы.")
        await callback.answer()
        return
    await callback.message.answer(
        "📚 Список модулей:", reply_markup=get_modules_admin_keyboard(modules)
    )
    await callback.answer()


# Просмотр выбранного модуля
@admin_router.callback_query(F.data.startswith("admin_view_module_"))
async def view_module(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])
    await callback.message.answer(
        f"📚 Управление модулем #{module_id}",
        reply_markup=get_module_management_keyboard(module_id),
    )
    await callback.answer()


"""
_____________________________________РЕДАКТИРОВАНИЕ МОДУЛЯ_________________________________________
"""


# Редактирование названия и описания модуля
@admin_router.callback_query(F.data.startswith("edit_module_title_and_desc_"))
async def edit_module(callback: CallbackQuery, state: FSMContext):
    module_id = int(callback.data.split("_")[-1])
    await state.update_data(module_id=module_id)
    await callback.message.answer(
        "Введите новое название модуля (или нажмите /skip):",
        reply_markup=get_back_keyboard(),
    )
    await callback.answer()
    await state.set_state(ModuleEditFSM.waiting_for_edit_module_title)


# Обработка нового названия
@admin_router.message(ModuleEditFSM.waiting_for_edit_module_title)
async def get_new_module_title(message: Message, state: FSMContext):
    if await is_back(message, state):
        return
    if message.text != "/skip":
        await state.update_data(new_title=message.text)
    await message.answer("Введите новое описание модуля (или нажмите /skip):")
    await state.set_state(ModuleEditFSM.waiting_for_edit_module_description)


# Обработка нового описания
@admin_router.message(ModuleEditFSM.waiting_for_edit_module_description)
async def get_new_module_description(message: Message, state: FSMContext):
    if await is_back(message, state):
        return
    if message.text == "/skip":
        new_description = ""
    new_description = message.text if message.text != "/skip" else ""
    data = await state.get_data()
    module_id = data.get("module_id")
    new_title = data.get("new_title", "")

    await db.update_module(module_id, new_title, new_description)
    await message.answer("✏️ Модуль обновлён!", reply_markup=get_admin_keyboard())
    await state.clear()


# Удаление модуля
@admin_router.callback_query(F.data.startswith("delete_module_"))
async def delete_selected_module(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Удалить модуль и относящиеся к нему уроки?",
        reply_markup=get_dangerous_accept_keyboard(callback.data),
    )
    await callback.answer()


# Обработчик подтверждения об удалении модуля
@admin_router.callback_query(F.data.startswith("accept_delete_module_"))
async def accept_module_deleting(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])
    await db.delete_module(module_id)
    await callback.message.answer("🗑 Модуль успешно удалён.")
    await callback.answer()
    modules = await db.get_all_modules()
    if not modules:
        await callback.message.answer("❗ Модулей больше нет.")
        return
    await callback.message.answer(
        "📚 Список модулей:", reply_markup=get_modules_admin_keyboard(modules)
    )


@admin_router.callback_query(F.data.startswith("cancel_delete_module_"))
async def cancel_module_deleting(callback: CallbackQuery):
    modules = await db.get_all_modules()
    await callback.message.answer(
        "📚 Список модулей:", reply_markup=get_modules_admin_keyboard(modules)
    )
    await callback.answer()


"""
_____________________________________СОЗДАНИЕ МОДУЛЯ_________________________________________
"""


# Обработчик кнопки "➕ Создать новый модуль"
@admin_router.callback_query(F.data == "create_new_module")
async def create_module(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "Введите название модуля 📚:", reply_markup=get_back_keyboard()
    )
    await callback.answer()
    await state.set_state(ModuleCreationFSM.waiting_for_module_title)


# Ввод названия модуля
@admin_router.message(ModuleCreationFSM.waiting_for_module_title)
async def get_module_title(message: Message, state: FSMContext):
    if await is_back(message, state):
        return
    await state.update_data(module_title=message.text)
    await message.answer("Теперь введите описание модуля 📝:")
    await state.set_state(ModuleCreationFSM.waiting_for_module_description)


# Ввод описания модуля
@admin_router.message(ModuleCreationFSM.waiting_for_module_description)
async def get_module_description(message: Message, state: FSMContext):
    if await is_back(message, state):
        return
    await state.update_data(module_description=message.text)
    await message.answer("Добавим первый урок! Введите название урока 📖:")
    await state.set_state(ModuleCreationFSM.waiting_for_lesson_title)


# Завершение модуля
@admin_router.callback_query(F.data == "finish_module")
async def start_test_creation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    module_title = data.get("module_title")
    module_description = data.get("module_description")
    lessons = data.get("lessons", [])

    if not module_title or not lessons:
        await callback.message.answer(
            "❗ Модуль не может быть создан без названия или уроков."
        )
        return

    # Создаём модуль без теста, чтобы сохранить ID для теста
    module_id = await db.create_module(module_title, module_description)
    await state.update_data(module_id=module_id)

    # Сохраняем уроки
    for order, lesson in enumerate(lessons, start=1):
        await db.add_lesson(
            module_id=module_id,
            title=lesson["title"],
            content=lesson["content"],
            file_ids=lesson["files"],
            video_ids=lesson["videos"],
            order=order,
        )

    await callback.message.answer(
        "Теперь создайте тест для модуля. Введите текст первого вопроса:",
        reply_markup=get_back_keyboard(),
    )
    await callback.answer()
    await state.update_data(in_module_creation=True)
    await state.set_state(TestCreationFSM.waiting_for_question)
