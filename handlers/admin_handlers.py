from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from filters import RoleFilter
from contexts import ModuleCreation
from aiogram.fsm.context import FSMContext
from keyboards.admin_keyboards import get_add_new_lesson_keyboard_markup
from keyboards.main_keyboards import admin_keyboard
from db import create_module, add_lesson

admin_router = Router()

# Старт создания модуля
@admin_router.message(RoleFilter("manager"), Command("create_module"))
async def start_module_creation(message: Message, state: FSMContext):
    await message.answer("Введите название модуля 📚:")
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
async def get_lesson_video(message: Message, state: FSMContext):
    data = await state.get_data()

    # Сохранение текущего урока
    lesson = {
        "title": data.get("lesson_title"),
        "content": data.get("lesson_text"),
        "files": data.get("lesson_files", []),
        "videos": [message.video.file_id]
    }

    lessons = data.get("lessons", [])
    lessons.append(lesson)
    await state.update_data(lessons=lessons)

    await message.answer("Видео добавлено! Добавить ещё урок или завершить модуль?",
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
    await state.set_state(ModuleCreation.waiting_for_lesson_title)

# Завершение модуля
@admin_router.callback_query(F.data == "finish_module")
async def finish_module(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Извлечение данных модуля
    module_title = data.get("module_title")
    module_description = data.get("module_description")
    lessons = data.get("lessons", [])

    if not module_title or not lessons:
        await callback.message.answer("❗ Модуль не может быть создан без названия или уроков.")
        return

    # Сохранение модуля в БД
    module_id = await create_module(module_title, module_description)

    # Сохранение уроков в БД
    for order, lesson in enumerate(lessons, start=1):
        lesson_title = lesson.get("title")
        lesson_content = lesson.get("content")
        lesson_files = lesson.get("files", [])
        lesson_videos = lesson.get("videos", [])

        await add_lesson(
            module_id=module_id,
            title=lesson_title,
            content=lesson_content,
            file_ids=lesson_files,
            video_ids=lesson_videos,
            order=order
        )

    # Уведомление об успешном создании
    await callback.message.answer(f"📚 Модуль '{module_title}' успешно создан!")
    await state.clear()


