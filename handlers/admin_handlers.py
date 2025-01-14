from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from filters import RoleFilter
from contexts import ModuleCreation
from aiogram.fsm.context import FSMContext
from keyboards.admin_keyboards import *

router = Router()

# Хендлер для менеджера
@router.message(CommandStart(), RoleFilter("manager"))
async def cmd_start(message: Message) -> None:
    await message.answer('Старт менеджер')


# Старт создания модуля
@router.message(RoleFilter("manager"), Command("create_module"))
async def start_module_creation(message: Message, state: FSMContext):
    await message.answer("Введите название модуля 📚:")
    await state.set_state(ModuleCreation.waiting_for_module_title)

# Ввод названия модуля
@router.message(ModuleCreation.waiting_for_module_title)
async def get_module_title(message: Message, state: FSMContext):
    await state.update_data(module_title=message.text)
    await message.answer("Теперь введите описание модуля 📝:")
    await state.set_state(ModuleCreation.waiting_for_module_description)

# Ввод описания модуля
@router.message(ModuleCreation.waiting_for_module_description)
async def get_module_description(message: Message, state: FSMContext):
    await state.update_data(module_description=message.text)
    await message.answer("Добавим первый урок! Введите название урока 📖:")
    await state.set_state(ModuleCreation.waiting_for_lesson_title)

# Ввод названия урока
@router.message(ModuleCreation.waiting_for_lesson_title)
async def get_lesson_title(message: Message, state: FSMContext):
    await state.update_data(lesson_title=message.text)
    await message.answer("Теперь введите текст для этого урока ✍️:")
    await state.set_state(ModuleCreation.waiting_for_lesson_text)

# Ввод текста урока
@router.message(ModuleCreation.waiting_for_lesson_text)
async def get_lesson_text(message: Message, state: FSMContext):
    await state.update_data(lesson_text=message.text)
    await message.answer("Загрузите файлы для урока 📎 (или напишите /skip):")
    await state.set_state(ModuleCreation.waiting_for_lesson_files)

# Загрузка файлов
@router.message(ModuleCreation.waiting_for_lesson_files, F.document)
async def get_lesson_files(message: Message, state: FSMContext):
    file_id = message.document.file_id
    data = await state.get_data()
    files = data.get("lesson_files", [])
    files.append(file_id)
    await state.update_data(lesson_files=files)
    await message.answer("Файл добавлен! Загружайте ещё или напишите /skip.")

# Пропуск загрузки файлов
@router.message(Command("skip"), ModuleCreation.waiting_for_lesson_files)
async def skip_lesson_files(message: Message, state: FSMContext):
    await message.answer("Теперь загрузите обучающее видео 🎥 (или напишите /skip):")
    await state.set_state(ModuleCreation.waiting_for_lesson_video)

# Загрузка видео
@router.message(ModuleCreation.waiting_for_lesson_video, F.video)
async def get_lesson_video(message: Message, state: FSMContext):
    await state.update_data(lesson_video=message.video.file_id)
    await message.answer("Видео добавлено! Добавить ещё урок или завершить модуль?",
                         reply_markup=get_add_new_lesson_keyboard_murkup())
    await state.set_state(ModuleCreation.waiting_for_next_action)

# Пропуск загрузки видео
@router.message(Command("skip"), ModuleCreation.waiting_for_lesson_video)
async def skip_lesson_video(message: Message, state: FSMContext):
    await message.answer("Добавить ещё урок или завершить модуль?",
                         reply_markup=get_add_new_lesson_keyboard_murkup())
    await state.set_state(ModuleCreation.waiting_for_next_action)

# Добавление нового урока
@router.callback_query(F.data == "add_lesson")
async def add_new_lesson(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название следующего урока 📖:")
    await state.set_state(ModuleCreation.waiting_for_lesson_title)

# Завершение модуля
@router.callback_query(F.data == "finish_module")
async def finish_module(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Здесь будет сохранение модуля и уроков в БД
    await callback.message.answer("📚 Модуль успешно создан!")
    await state.clear()