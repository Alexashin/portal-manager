from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm import FSMContext
from db.db_controller import get_all_modules, get_lessons_by_module
from filters.role_filter import RoleFilter

user_router = Router()

# Команда для отображения модулей
@user_router.message(RoleFilter("intern"), F.text == "/modules")
async def show_modules(message: Message):
    modules = await get_all_modules()
    
    if not modules:
        await message.answer("📚 Пока нет доступных модулей.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=module['title'], callback_data=f"open_module_{module['id']}")]
            for module in modules
        ]
    )

    await message.answer("Выберите модуль для изучения:", reply_markup=keyboard)

# Обработка выбора модуля
@user_router.callback_query(F.data.startswith("open_module_"))
async def open_module(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])
    lessons = await get_lessons_by_module(module_id)

    if not lessons:
        await callback.message.answer("❗ У этого модуля пока нет уроков.")
        return

    # Отображаем первый урок
    await send_lesson(callback.message, lessons, 0)

# Отправка урока
async def send_lesson(message: Message, lessons, index):
    lesson = lessons[index]
    total_lessons = len(lessons)

    text = f"<b>{lesson['title']}</b>\n\n{lesson['content']}"
    
    # Кнопки навигации
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"lesson_{index - 1}"))
    if index < total_lessons - 1:
        buttons.append(InlineKeyboardButton(text="➡️ Вперёд", callback_data=f"lesson_{index + 1}"))
    buttons.append(InlineKeyboardButton(text="✅ Завершить", callback_data="finish_lesson"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

    await message.answer(text, reply_markup=keyboard)

    # Отправка файлов
    for file_id in lesson.get('file_ids', []):
        await message.answer_document(file_id)

    # Отправка видео
    for video_id in lesson.get('video_ids', []):
        await message.answer_video(video_id)

# Навигация по урокам
@user_router.callback_query(F.data.startswith("lesson_"))
async def navigate_lessons(callback: CallbackQuery, state: FSMContext):
    _, module_id, index = callback.data.split("_")
    lessons = await get_lessons_by_module(int(module_id))
    await send_lesson(callback.message, lessons, int(index))

# Завершение модуля
@user_router.callback_query(F.data == "finish_lesson")
async def finish_lesson(callback: CallbackQuery):
    await callback.message.answer("🎉 Вы завершили изучение модуля!")

@user_router.message(F.text == "📖 Материалы")
async def show_materials(message: Message):
    await message.answer("📖 Вот доступные материалы...")