from aiogram_run import bot
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import db
from keyboards import *
from filters import RoleFilter

employee_router = Router()


# Старт для сотрудника
@employee_router.message(RoleFilter("employee"), F.text == "/start")
async def employee_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в рабочий портал!", reply_markup=get_employee_keyboard()
    )


# Показ доступных модулей
@employee_router.message(RoleFilter("employee"), F.text == "📖 Материалы")
async def show_modules(message: Message):
    modules = await db.get_all_modules()

    if not modules:
        await message.answer("❗ В системе пока нет доступных материалов.")
        return

    await message.answer(
        "📚 Доступные материалы:", reply_markup=get_avaible_modules_keyboard(modules)
    )


# Открытие выбранного модуля
@employee_router.callback_query(
    RoleFilter("employee"), F.data.startswith("open_module_")
)
async def open_module(callback: CallbackQuery, state: FSMContext):
    module_id = int(callback.data.split("_")[-1])
    lessons = await db.get_lessons_by_module(module_id)

    if not lessons:
        await callback.message.answer("❗ В этом модуле пока нет уроков.")
        return

    await state.update_data(module_id=module_id, lesson_index=0)
    await callback.message.answer(
        "Начато изучение материалов!", reply_markup=get_back_keyboard()
    )
    
    data = await state.get_data()
    temporary_msgs = data.get("temporary_msgs", [])
    if temporary_msgs != []:
        for msg_id in temporary_msgs:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)
        await state.update_data(temporary_msgs=[])
        
    await send_lesson(callback.message, state, 0, module_id)


# Навигация по урокам модуля
@employee_router.callback_query(
    RoleFilter("employee"), F.data.startswith("open_lesson_")
)
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
    lessons = await db.get_lessons_by_module(module_id)
    lesson = lessons[index]
    total_lessons = len(lessons)
    
    text = f"<b>{lesson['title']}</b>\nФайлы урока:"

    buttons = []
    if index > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"open_lesson_{module_id}_{index - 1}"
            )
        )
    if index < total_lessons - 1:
        buttons.append(
            InlineKeyboardButton(
                text="➡️ Вперёд", callback_data=f"open_lesson_{module_id}_{index + 1}"
            )
        )
    buttons.append(
        InlineKeyboardButton(
            text="✅ Завершить просмотр", callback_data=f"finish_viewing_{module_id}"
        )
    )

    data = await state.get_data()
    new_temporary_msgs = data.get("temporary_msgs", [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    msg = await message.answer(text)
    new_temporary_msgs.append(msg.message_id)
    for file_id in lesson.get("file_ids", []):
        msg = await message.answer_document(file_id)
        new_temporary_msgs.append(msg.message_id)
    for video_id in lesson.get("video_ids", []):
        msg = await message.answer_video(video_id)
        new_temporary_msgs.append(msg.message_id)
    msg = await message.answer(f"{lesson['content']}")
    new_temporary_msgs.append(msg.message_id)
    msg = await message.answer("<b>Продолжим?</b>", reply_markup=keyboard)
    new_temporary_msgs.append(msg.message_id)
    await state.update_data(temporary_msgs=new_temporary_msgs)


# Завершение просмотра модуля (без тестов)
@employee_router.callback_query(
    RoleFilter("employee"), F.data.startswith("finish_viewing_")
)
async def finish_viewing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    temporary_msgs = data.get("temporary_msgs", [])
    for msg_id in temporary_msgs:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)
    
    await callback.message.answer(
        "✅ Вы завершили просмотр модуля.", reply_markup=get_employee_keyboard()
    )
    await state.clear()
