import db
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from contexts import ModuleCreationFSM, ModuleEditFSM
from keyboards import (
    get_lessons_management_keyboard,
    get_lesson_management_keyboard,
    get_admin_keyboard,
    get_back_keyboard,
    get_add_new_lesson_keyboard_markup,
    get_dangerous_accept_keyboard,
)
from handlers.admin.main_handlers import is_back

admin_router = Router()

log = logging.getLogger(__name__)


# Показ уроков модуля
@admin_router.callback_query(F.data.startswith("manage_lessons_"))
async def manage_lessons(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])
    lessons = await db.get_lessons_by_module(module_id)

    if not lessons:
        await callback.message.answer("❗ В этом модуле пока нет уроков.")
        await callback.answer()
        return

    await callback.message.answer(
        "📖 Уроки модуля:",
        reply_markup=get_lessons_management_keyboard(module_id, lessons),
    )
    await callback.answer()


# Показ уроков модуля
@admin_router.callback_query(F.data.startswith("manage_lesson_"))
async def manage_lesson(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[-1])
    await callback.message.answer(
        "📖 Выбор действия:", reply_markup=get_lesson_management_keyboard(lesson_id)
    )
    await callback.answer()


"""
_____________________________________СОЗДАНИЕ УРОКА_________________________________________
"""


# Добавление нового урока
@admin_router.callback_query(F.data == "add_lesson")
async def add_new_lesson(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название следующего урока 📖:")
    await callback.answer()
    await state.set_state(ModuleCreationFSM.waiting_for_lesson_title)


# Добавление урока в модуль
@admin_router.callback_query(F.data.startswith("add_lesson_"))
async def add_lesson_to_module(callback: CallbackQuery, state: FSMContext):
    module_id = int(callback.data.split("_")[-1])
    await state.update_data(module_id=module_id)
    await callback.message.answer(
        "Введите название урока 📖:", reply_markup=get_back_keyboard()
    )
    await callback.answer()
    await state.set_state(ModuleCreationFSM.waiting_for_lesson_title)


# Ввод названия урока
@admin_router.message(ModuleCreationFSM.waiting_for_lesson_title)
async def get_lesson_title(message: Message, state: FSMContext):
    if await is_back(message, state):
        return
    await state.update_data(lesson_title=message.text)
    await message.answer("Теперь введите текст для этого урока ✍️:")
    await state.set_state(ModuleCreationFSM.waiting_for_lesson_text)


# Ввод текста урока
@admin_router.message(ModuleCreationFSM.waiting_for_lesson_text)
async def get_lesson_text(message: Message, state: FSMContext):
    if await is_back(message, state):
        return
    await state.update_data(lesson_text=message.text)
    await message.answer("Загрузите файлы для урока 📎 (или напишите /skip):")
    await state.set_state(ModuleCreationFSM.waiting_for_lesson_files)


# Загрузка файлов
@admin_router.message(ModuleCreationFSM.waiting_for_lesson_files, F.document)
async def get_lesson_files(message: Message, state: FSMContext):
    file_id = message.document.file_id
    data = await state.get_data()
    files = data.get("lesson_files", [])
    files.append(file_id)
    await state.update_data(lesson_files=files)
    await message.answer("Файл добавлен! Загружайте ещё или напишите /skip.")


# Пропуск загрузки файлов
@admin_router.message(Command("skip"), ModuleCreationFSM.waiting_for_lesson_files)
async def skip_lesson_files(message: Message, state: FSMContext):
    await message.answer("Теперь загрузите обучающее видео 🎥 (или напишите /skip):")
    await state.set_state(ModuleCreationFSM.waiting_for_lesson_video)


# Загрузка видео
@admin_router.message(ModuleCreationFSM.waiting_for_lesson_video, F.video)
async def get_lesson_video(message: Message, state: FSMContext):
    video_id = message.video.file_id
    data = await state.get_data()
    videos = data.get("lesson_videos", [])
    videos.append(video_id)
    await state.update_data(lesson_videos=videos)
    await message.answer("Видео добавлено! Загружайте ещё или напишите /skip.")


# Пропуск загрузки видео
@admin_router.message(Command("skip"), ModuleCreationFSM.waiting_for_lesson_video)
async def skip_lesson_video(message: Message, state: FSMContext):
    data = await state.get_data()
    module_id = data.get("module_id", "")
    if module_id != "":
        title = data.get("lesson_title")
        content = data.get("lesson_text")
        file_ids = data.get("lesson_files", [])
        video_ids = data.get("lesson_videos", [])
        await db.add_new_lesson_to_module(
            module_id, title, content, file_ids, video_ids
        )
        await message.answer("Урок добавлен!", reply_markup=get_admin_keyboard())
        await state.clear()
        return
    videos = data.get("lesson_videos", [])

    if videos != []:
        # Сохранение текущего урока
        lesson = {
            "title": data.get("lesson_title"),
            "content": data.get("lesson_text"),
            "files": data.get("lesson_files", []),
            "videos": videos,
        }
    else:
        lesson = {
            "title": data.get("lesson_title"),
            "content": data.get("lesson_text"),
            "files": data.get("lesson_files", []),
            "videos": [],
        }

    lessons = data.get("lessons", [])
    lessons.append(lesson)
    await state.update_data(
        lessons=lessons,
        lesson_title="",
        lesson_text="",
        lesson_files=[],
        lesson_videos=[],
    )
    await message.answer(
        "Отлично! Добавить ещё урок или завершить модуль?",
        reply_markup=get_add_new_lesson_keyboard_markup(),
    )
    await state.set_state(ModuleCreationFSM.waiting_for_next_action)


"""
_____________________________________ПРОСМОТР УРОКА_____________________________________
"""


@admin_router.callback_query(F.data.startswith("view_lesson_"))
async def view_lesson_content(callback: CallbackQuery):
    """
    Обработчик для просмотра урока модератором.
    """
    lesson_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    # Получаем данные урока
    lesson = await db.get_lesson_by_id(lesson_id)
    if not lesson:
        await callback.message.answer("❗ Урок не найден.")
        await callback.answer()
        return

    # Логируем действие модератора
    log.info(f"Модератор {user_id} посмотрел урок {lesson_id}.")

    # Формируем сообщение для отправки
    text = f"📖 <b>{lesson['title']}</b>\n\n{lesson['content']}\n\n"

    # Проверяем файлы и видео
    if lesson.get("file_ids"):
        text += "📎 В этом уроке есть прикрепленные файлы.\n"
    if lesson.get("video_ids"):
        text += "🎥 В этом уроке есть видео.\n"

    # Отправляем информацию модератору
    await callback.message.answer(text, parse_mode="HTML")

    # Если есть файлы, отправляем их отдельно
    for file_id in lesson.get("file_ids", []):
        try:
            await callback.message.answer_document(file_id)
        except Exception as ex:
            log.error(f"Ошибка отправки файла! Урок id #{lesson_id}: {ex}")
            await callback.message.answer("Ошибка отправки файла!")
    # Если есть видео, отправляем его отдельно
    for video_id in lesson.get("video_ids", []):
        try:
            await callback.message.answer_video(video_id)
        except Exception as ex:
            log.error(f"Ошибка отправки видео! Урок id #{lesson_id}: {ex}")
            await callback.message.answer("Ошибка отправки видео!")
    await callback.answer()


"""
_____________________________________РЕДАКТИРОВАНИЕ УРОКА_________________________________________
"""


# Начало редактирования урока
@admin_router.callback_query(F.data.startswith("edit_lesson_"))
async def edit_lesson(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split("_")[-1])
    await state.update_data(lesson_edit_id=lesson_id)
    await callback.message.answer(
        "Введите новое название урока:", reply_markup=get_back_keyboard()
    )
    await state.set_state(ModuleEditFSM.waiting_for_edit_lesson_title)
    await callback.answer()


# Редактирование названия урока
@admin_router.message(ModuleEditFSM.waiting_for_edit_lesson_title, F.text)
async def edit_lesson_title(message: Message, state: FSMContext):
    if await is_back(message, state):
        return
    if message.text.strip().lower() == "/skip":
        await message.answer("Введите новый текст урока (или нажмите /skip):")
    else:
        await state.update_data(new_lesson_title=message.text.strip())
        await message.answer("Введите новый текст урока:")
    await state.set_state(ModuleEditFSM.waiting_for_edit_lesson_text)


# Редактирование текста урока
@admin_router.message(ModuleEditFSM.waiting_for_edit_lesson_text, F.text)
async def edit_lesson_text(message: Message, state: FSMContext):
    if await is_back(message, state):
        return
    if message.text.strip().lower() == "/skip":
        await message.answer(
            "Загрузите новые файлы для урока 📎 (или напишите /skip для удаления):"
        )
    else:
        await state.update_data(new_lesson_text=message.text.strip())
        await message.answer(
            "Загрузите новые файлы для урока 📎 (или напишите /skip для удаления):"
        )
    await state.set_state(ModuleEditFSM.waiting_for_edit_lesson_files)


# Добавление файлов
@admin_router.message(ModuleEditFSM.waiting_for_edit_lesson_files, F.document)
async def edit_lesson_files(message: Message, state: FSMContext):
    file_id = message.document.file_id
    data = await state.get_data()
    new_files = data.get("new_lesson_files", [])
    new_files.append(file_id)
    await state.update_data(new_lesson_files=new_files)
    await message.answer(
        "Файл добавлен! Загружайте ещё или напишите /skip для продолжения"
    )


# Пропуск добавления файлов
@admin_router.message(Command("skip"), ModuleEditFSM.waiting_for_edit_lesson_files)
async def skip_files(message: Message, state: FSMContext):
    await message.answer(
        "Загрузите обучающее видео 🎥 (или напишите /skip для удаления):"
    )
    await state.set_state(ModuleEditFSM.waiting_for_edit_lesson_video)


# Добавление видео
@admin_router.message(ModuleEditFSM.waiting_for_edit_lesson_video, F.video)
async def edit_lesson_videos(message: Message, state: FSMContext):
    video_id = message.video.file_id
    data = await state.get_data()
    new_videos = data.get("new_lesson_videos", [])
    new_videos.append(video_id)
    await state.update_data(new_lesson_videos=new_videos)
    await message.answer(
        "Видео добавлено! Загружайте ещё или напишите /skip для завершения"
    )


# Пропуск добавления видео
@admin_router.message(Command("skip"), ModuleEditFSM.waiting_for_edit_lesson_video)
async def skip_videos(message: Message, state: FSMContext):
    await save_edited_lesson(message, state)


# Завершение редактирования
async def save_edited_lesson(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.update_lesson(
        lesson_id=data.get("lesson_edit_id"),
        new_title=data.get("new_lesson_title", ""),
        new_content=data.get("new_lesson_text", ""),
        new_file_ids=data.get("new_lesson_files", []),
        new_video_ids=data.get("new_lesson_videos", []),
    )
    await message.answer("✅ Урок обновлён.", reply_markup=get_admin_keyboard())
    await state.clear()


@admin_router.callback_query(F.data.startswith("delete_lesson_"))
async def confirm_delete_lesson(callback: CallbackQuery):
    await callback.message.answer(
        "Вы уверены, что хотите удалить этот урок?",
        reply_markup=get_dangerous_accept_keyboard(callback.data),
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("accept_delete_lesson_"))
async def delete_lesson(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[-1])
    await db.delete_lesson(lesson_id)
    log.info(f"Пользователь {callback.message.from_user.id} удалил урок #{lesson_id}")
    await callback.message.answer("🗑 Урок успешно удалён.")
    await callback.answer()


# Удаление урока
@admin_router.callback_query(F.data.startswith("cancel_delete_lesson_"))
async def delete_selected_lesson(callback: CallbackQuery):
    await callback.message.answer("🗑 Отмена.")
    await callback.answer()
