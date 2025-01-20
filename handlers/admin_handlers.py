from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from filters import RoleFilter
from contexts import ModuleCreation, ModuleEdit
from keyboards import *
import db

admin_router = Router()

"""
_____________________________________ОСНОВНЫЕ ХЕНДЛЕРЫ_________________________________________
"""

# Обработчик кнопки "🔙 Назад"
@admin_router.message(RoleFilter("manager"), F.text == "🔙 Назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=get_admin_keyboard())

# Обработчик кнопки "📚 Управление обучением"
@admin_router.message(RoleFilter("manager"), F.text == "📚 Управление обучением")
async def manage_training(message: Message):
    await message.answer("Выберите действие:", reply_markup=get_training_management_inline_keyboard())

# Обработчик кнопки "👥 Пользователи"
@admin_router.message(RoleFilter("manager"), F.text == "👥 Пользователи")
async def view_users(message: Message):
    await message.answer("📋 Список пользователей будет здесь.")

# Обработчик кнопки "📊 Статистика"
@admin_router.message(RoleFilter("manager"), F.text == "📊 Статистика")
async def view_statistics(message: Message):
    await message.answer("📈 Статистика будет здесь.")

# Показ списка модулей
@admin_router.callback_query(RoleFilter("manager"), F.data == "list_modules")
async def show_modules(callback: CallbackQuery):
    modules = await db.get_all_modules()
    if not modules:
        await callback.message.answer("❗ Модули пока не созданы.")
        await callback.answer()
        return
    await callback.message.answer("📚 Список модулей:", reply_markup=get_modules_admin_keyboard(modules))
    await callback.answer()

# Просмотр выбранного модуля
@admin_router.callback_query(F.data.startswith("admin_view_module_"))
async def view_module(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])
    await callback.message.answer(f"📚 Управление модулем #{module_id}", reply_markup=get_module_management_keyboard(module_id))
    await callback.answer()

# Показ уроков модуля
@admin_router.callback_query(F.data.startswith("manage_lessons_"))
async def manage_lessons(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])
    lessons = await db.get_lessons_by_module(module_id)

    if not lessons:
        await callback.message.answer("❗ В этом модуле пока нет уроков.")
        await callback.answer()
        return

    await callback.message.answer("📖 Уроки модуля:", reply_markup=get_lessons_management_keyboard(module_id, lessons))
    await callback.answer()


# Показ уроков модуля
@admin_router.callback_query(F.data.startswith("view_lesson_"))
async def manage_lesson(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[-1])
    await callback.message.answer("📖 Выбор действия:", reply_markup=get_lesson_management_keyboard(lesson_id))
    await callback.answer()

"""
_____________________________________РЕДАКТИРОВАНИЕ МОДУЛЯ_________________________________________
"""

# Редактирование названия и описания модуля
@admin_router.callback_query(F.data.startswith("edit_module_title_and_desc_"))
async def edit_module(callback: CallbackQuery, state: FSMContext):
    module_id = int(callback.data.split("_")[-1])
    await state.update_data(module_id=module_id)
    await callback.message.answer("Введите новое название модуля (или нажмите /skip):", reply_markup=get_back_keyboard())
    await callback.answer()
    await state.set_state(ModuleEdit.waiting_for_edit_module_title)

# Обработка нового названия
@admin_router.message(ModuleEdit.waiting_for_edit_module_title)
async def save_edited_module(message: Message, state: FSMContext):
    if message.text != "/skip":
        await state.update_data(new_title=message.text)
    await message.answer("Введите новое описание модуля (или нажмите /skip):")
    await state.set_state(ModuleEdit.waiting_for_edit_module_description)

# Обработка нового описания
@admin_router.message(ModuleEdit.waiting_for_edit_module_description)
async def save_edited_module(message: Message, state: FSMContext):
    if message.text == "/skip":
        new_description = ''
    new_description = message.text if message.text != "/skip" else ''
    data = await state.get_data()
    module_id = data.get("module_id")
    new_title = data.get("new_title", '')
    
    await db.update_module(module_id, new_title, new_description)
    await message.answer(f"✏️ Модуль обновлён!", reply_markup=get_admin_keyboard())
    await state.clear()

# Удаление модуля
@admin_router.callback_query(F.data.startswith("delete_module_"))
async def delete_selected_module(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Удалить модуль и относящиеся к нему уроки?", reply_markup=get_dangerous_accept_keyboard(callback.data))
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
    await callback.message.answer("📚 Список модулей:", reply_markup=get_modules_admin_keyboard(modules))

@admin_router.callback_query(F.data.startswith("cancel_delete_module_"))
async def cancel_module_deleting(callback: CallbackQuery):
    modules = await db.get_all_modules()
    await callback.message.answer("📚 Список модулей:", reply_markup=get_modules_admin_keyboard(modules))
    await callback.answer()

"""
_____________________________________СОЗДАНИЕ МОДУЛЯ_________________________________________
"""

# Обработчик кнопки "➕ Создать новый модуль"
@admin_router.callback_query(F.data == "create_new_module")
async def create_module(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Введите название модуля 📚:", reply_markup=get_back_keyboard())
    await callback.answer()
    await state.set_state(ModuleCreation.waiting_for_module_title)

# Ввод названия модуля
@admin_router.message(ModuleCreation.waiting_for_module_title)
async def get_module_title(message: Message, state: FSMContext):
    await state.update_data(module_title=message.text)
    await message.answer("Теперь введите описание модуля 📝:")
    await state.set_state(ModuleCreation.waiting_for_module_description)

# Ввод описания модуля
@admin_router.message(ModuleCreation.waiting_for_module_description)
async def get_module_description(message: Message, state: FSMContext):
    await state.update_data(module_description=message.text)
    await message.answer("Добавим первый урок! Введите название урока 📖:")
    await state.set_state(ModuleCreation.waiting_for_lesson_title)

"""
_____________________________________СОЗДАНИЕ УРОКА_________________________________________
"""

# Ввод названия урока
@admin_router.message(ModuleCreation.waiting_for_lesson_title)
async def get_lesson_title(message: Message, state: FSMContext):
    await state.update_data(lesson_title=message.text)
    await message.answer("Теперь введите текст для этого урока ✍️:")
    await state.set_state(ModuleCreation.waiting_for_lesson_text)

# Ввод текста урока
@admin_router.message(ModuleCreation.waiting_for_lesson_text)
async def get_lesson_text(message: Message, state: FSMContext):
    await state.update_data(lesson_text=message.text)
    await message.answer("Загрузите файлы для урока 📎 (или напишите /skip):")
    await state.set_state(ModuleCreation.waiting_for_lesson_files)

# Загрузка файлов
@admin_router.message(ModuleCreation.waiting_for_lesson_files, F.document)
async def get_lesson_files(message: Message, state: FSMContext):
    file_id = message.document.file_id
    data = await state.get_data()
    files = data.get("lesson_files", [])
    files.append(file_id)
    await state.update_data(lesson_files=files)
    await message.answer("Файл добавлен! Загружайте ещё или напишите /skip.")

# Пропуск загрузки файлов
@admin_router.message(Command("skip"), ModuleCreation.waiting_for_lesson_files)
async def skip_lesson_files(message: Message, state: FSMContext):
    await message.answer("Теперь загрузите обучающее видео 🎥 (или напишите /skip):")
    await state.set_state(ModuleCreation.waiting_for_lesson_video)

# Загрузка видео
@admin_router.message(ModuleCreation.waiting_for_lesson_video, F.video)
async def get_lesson_files(message: Message, state: FSMContext):
    video_id = message.video.file_id
    data = await state.get_data()
    videos = data.get("lesson_videos", [])
    videos.append(video_id)
    await state.update_data(lesson_videos=videos)
    await message.answer("Видео добавлено! Загружайте ещё или напишите /skip.")
    
# Пропуск загрузки видео
@admin_router.message(Command("skip"), ModuleCreation.waiting_for_lesson_video)
async def get_lesson_video(message: Message, state: FSMContext):
    data = await state.get_data()

    videos = data.get("lesson_videos", [])
    
    if videos != []:
        # Сохранение текущего урока
        lesson = {
            "title": data.get("lesson_title"),
            "content": data.get("lesson_text"),
            "files": data.get("lesson_files", []),
            "videos": videos
        }
    else:
        lesson = {
        "title": data.get("lesson_title"),
        "content": data.get("lesson_text"),
        "files": data.get("lesson_files", []),
        "videos": []
        }

    lessons = data.get("lessons", [])
    lessons.append(lesson)
    await state.update_data(lessons=lessons)

    await message.answer("Отлично! Добавить ещё урок или завершить модуль?",
                         reply_markup=get_add_new_lesson_keyboard_markup())
    await state.set_state(ModuleCreation.waiting_for_next_action)

# Пропуск загрузки видео
@admin_router.message(Command("skip"), ModuleCreation.waiting_for_lesson_video)
async def skip_lesson_video(message: Message, state: FSMContext):
    data = await state.get_data()

    # Сохранение текущего урока без видео
    lesson = {
        "title": data.get("lesson_title"),
        "content": data.get("lesson_text"),
        "files": data.get("lesson_files", []),
        "videos": []
    }

    lessons = data.get("lessons", [])
    lessons.append(lesson)
    await state.update_data(lessons=lessons)

    await message.answer("Добавить ещё урок или завершить модуль?",
                         reply_markup=get_add_new_lesson_keyboard_markup())
    await state.set_state(ModuleCreation.waiting_for_next_action)

# Добавление нового урока
@admin_router.callback_query(F.data == "add_lesson")
async def add_new_lesson(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название следующего урока 📖:")
    await callback.answer()
    await state.set_state(ModuleCreation.waiting_for_lesson_title)

# Завершение модуля
@admin_router.callback_query(F.data == "finish_module", ModuleCreation.waiting_for_next_action)
async def finish_module(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # Извлечение данных модуля
    module_title = data.get("module_title")
    module_description = data.get("module_description")
    lessons = data.get("lessons", [])

    if not module_title or not lessons:
        await callback.message.answer("❗ Модуль не может быть создан без названия или уроков.")
        await callback.answer()
        return

    # Сохранение модуля в БД
    module_id = await db.create_module(module_title, module_description)

    # Сохранение уроков в БД
    for order, lesson in enumerate(lessons, start=1):
        lesson_title = lesson.get("title")
        lesson_content = lesson.get("content")
        lesson_files = lesson.get("files", [])
        lesson_videos = lesson.get("videos", [])

        await db.add_lesson(
            module_id=module_id,
            title=lesson_title,
            content=lesson_content,
            file_ids=lesson_files,
            video_ids=lesson_videos,
            order=order
        )

    # Уведомление об успешном создании
    await callback.message.answer(f"📚 Модуль '{module_title}' успешно создан!", reply_markup=get_admin_keyboard())
    await callback.answer()
    await state.clear() 

"""
_____________________________________РЕДАКТИРОВАНИЕ УРОКА_________________________________________
"""

# Начало редактирования урока
@admin_router.callback_query(F.data.startswith("edit_lesson_"))
async def edit_lesson(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split("_")[-1])
    await state.update_data(lesson_edit_id=lesson_id)
    await callback.message.answer("Введите новое название урока:", reply_markup=get_back_keyboard())
    await state.set_state(ModuleEdit.waiting_for_edit_lesson_title)
    await callback.answer()

# Редактирование названия урока
@admin_router.message(ModuleEdit.waiting_for_edit_lesson_title, F.text)
async def edit_lesson_title(message: Message, state: FSMContext):
    if message.text.strip().lower() == "/skip":
        await message.answer("Введите новый текст урока (или нажмите /skip):")
    else:
        await state.update_data(new_lesson_title=message.text.strip())
        await message.answer("Введите новый текст урока:")
    await state.set_state(ModuleEdit.waiting_for_edit_lesson_text)

# Редактирование текста урока
@admin_router.message(ModuleEdit.waiting_for_edit_lesson_text, F.text)
async def edit_lesson_text(message: Message, state: FSMContext):
    if message.text.strip().lower() == "/skip":
        await message.answer("Загрузите новые файлы для урока 📎 (или напишите /skip для удаления):")
    else:
        await state.update_data(new_lesson_text=message.text.strip())
        await message.answer("Загрузите новые файлы для урока 📎 (или напишите /skip для удаления):")
    await state.set_state(ModuleEdit.waiting_for_edit_lesson_files)

# Добавление файлов
@admin_router.message(ModuleEdit.waiting_for_edit_lesson_files, F.document)
async def edit_lesson_files(message: Message, state: FSMContext):
    file_id = message.document.file_id
    data = await state.get_data()
    new_files = data.get("new_lesson_files", [])
    new_files.append(file_id)
    await state.update_data(new_lesson_files=new_files)
    await message.answer("Файл добавлен! Загружайте ещё или напишите /skip для продолжения")

# Пропуск добавления файлов
@admin_router.message(Command("skip"), ModuleEdit.waiting_for_edit_lesson_files)
async def skip_files(message: Message, state: FSMContext):
    await message.answer("Загрузите обучающее видео 🎥 (или напишите /skip для удаления):")
    await state.set_state(ModuleEdit.waiting_for_edit_lesson_video)

# Добавление видео
@admin_router.message(ModuleEdit.waiting_for_edit_lesson_video, F.video)
async def edit_lesson_videos(message: Message, state: FSMContext):
    video_id = message.video.file_id
    data = await state.get_data()
    new_videos = data.get("new_lesson_videos", [])
    new_videos.append(video_id)
    await state.update_data(new_lesson_videos=new_videos)
    await message.answer("Видео добавлено! Загружайте ещё или напишите /skip для завершения")

# Пропуск добавления видео
@admin_router.message(Command("skip"), ModuleEdit.waiting_for_edit_lesson_video)
async def skip_videos(message: Message, state: FSMContext):
    await save_edited_lesson(message, state)

# Завершение редактирования
async def save_edited_lesson(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.update_lesson(
        lesson_id=data.get('lesson_edit_id'),
        new_title=data.get('new_lesson_title', ''),
        new_content=data.get('new_lesson_text', ''),
        new_file_ids=data.get('new_lesson_files', []),
        new_video_ids=data.get('new_lesson_videos', [])
    )
    await message.answer("✅ Урок обновлён.", reply_markup=get_admin_keyboard())
    await state.clear()


@admin_router.callback_query(F.data.startswith("delete_lesson_"))
async def confirm_delete_lesson(callback: CallbackQuery):
    await callback.message.answer("Вы уверены, что хотите удалить этот урок?", reply_markup=get_dangerous_accept_keyboard(callback.data))
    await callback.answer()

@admin_router.callback_query(F.data.startswith('accept_delete_lesson_'))
async def delete_lesson(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[-1])
    await db.delete_lesson(lesson_id)
    await callback.message.answer("🗑 Урок успешно удалён.")
    await callback.answer()

# Удаление урока
@admin_router.callback_query(F.data.startswith("cancel_delete_lesson_"))
async def delete_selected_lesson(callback: CallbackQuery):
    await callback.message.answer("🗑 Отмена.")
    await callback.answer()
