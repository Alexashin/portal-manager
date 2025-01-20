from aiogram_run import bot
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from filters import RoleFilter
from db import get_all_modules, get_lessons_by_module
from keyboards import get_back_keyboard, get_intern_keyboard

intern_router = Router()

# Обработчик кнопки "🔙 Назад"
@intern_router.message(RoleFilter("intern"), F.text == "🔙 Назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=get_intern_keyboard())

# Показ доступных модулей для стажёра
@intern_router.message(RoleFilter("intern"), F.text == "📖 Доступные модули")
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
    await message.answer("Модули для обучения:", reply_markup=keyboard)


# Открытие выбранного модуля
@intern_router.callback_query(F.data.startswith("open_module_"))
async def open_module(callback: CallbackQuery, state: FSMContext):
    module_id = int(callback.data.split("_")[-1])
    lessons = await get_lessons_by_module(module_id)

    if not lessons:
        await callback.message.answer("❗ В этом модуле пока нет уроков.")
        return
    await state.update_data(module_id=module_id, lesson_index=0)
    await callback.message.answer("Начато обучение!", reply_markup=get_back_keyboard())
    data = await state.get_data()
    temporary_msgs = data.get("temporary_msgs", [])
    if temporary_msgs != []:
        for msg_id in temporary_msgs:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)
        await state.update_data(temporary_msgs=[])
    await send_lesson(callback.message, state, 0, module_id)

@intern_router.callback_query(F.data.startswith("open_lesson_"))
async def change_lesson(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split("_")[-1])
    module_id = int(callback.data.split("_")[-2])
    data = await state.get_data()
    temporary_msgs = data.get("temporary_msgs", [])
    if temporary_msgs != []:
        for msg_id in temporary_msgs:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)
        await state.update_data(temporary_msgs=[])
    await send_lesson(callback.message, state, lesson_id, module_id)

# Отправка урока с навигацией
async def send_lesson(message: Message, state: FSMContext, index, module_id):
    lessons = await get_lessons_by_module(module_id)
    lesson = lessons[index]
    total_lessons = len(lessons)

    text = f"<b>{lesson['title']}</b>\nФайлы урока:"

    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"open_lesson_{module_id}_{index - 1}"))
    if index < total_lessons - 1:
        buttons.append(InlineKeyboardButton(text="➡️ Вперёд", callback_data=f"open_lesson_{module_id}_{index + 1}"))
    buttons.append(InlineKeyboardButton(text="✅ Завершить", callback_data=f"finish_module_{module_id}"))

    data = await state.get_data()
    new_temporary_msgs = data.get('temporary_msgs', [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    msg = await message.answer(text)
    new_temporary_msgs.append(msg.message_id)
    for file_id in lesson.get('file_ids', []):
        msg = await message.answer_document(file_id)
        new_temporary_msgs.append(msg.message_id)

    for video_id in lesson.get('video_ids', []):
        msg = await message.answer_video(video_id)
        new_temporary_msgs.append(msg.message_id)
    msg = await message.answer(f"{lesson['content']}")
    new_temporary_msgs.append(msg.message_id)
    msg = await message.answer("<b>Продолжим?</b>", reply_markup=keyboard)
    new_temporary_msgs.append(msg.message_id)
    await state.update_data(temporary_msgs=new_temporary_msgs)

# Завершение модуля
@intern_router.callback_query(F.data.startswith("finish_module_"))
async def finish_module(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    temporary_msgs = data.get("temporary_msgs", [])
    for msg_id in temporary_msgs:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)
    await state.clear()
    await callback.message.answer("🎉 Поздравляем! Вы завершили изучение модуля!", reply_markup=get_intern_keyboard())
