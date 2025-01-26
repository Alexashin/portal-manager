from aiogram_run import bot
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from filters import RoleFilter
import db
from keyboards import get_back_keyboard, get_intern_keyboard

intern_router = Router()


# Обработчик кнопки "🔙 Назад"
@intern_router.message(RoleFilter("intern"), F.text == "🔙 Назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню.", reply_markup=get_intern_keyboard()
    )


# Показ доступных модулей для стажёра
@intern_router.message(RoleFilter("intern"), F.text == "📖 Доступные модули")
async def show_modules(message: Message):
    user_id = message.from_user.id
    modules = await db.get_available_modules_for_user(user_id)

    if not modules:
        await message.answer("📚 Пока нет доступных модулей.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=module["title"], callback_data=f"open_module_{module['id']}"
                )
            ]
            for module in modules
        ]
    )
    await message.answer("Модули для обучения:", reply_markup=keyboard)


# Отображение прогресса
@intern_router.message(RoleFilter("intern"), F.text == "📊 Мой прогресс")
async def show_progress(message: Message):
    user_id = message.from_user.id
    progress = await db.get_user_progress(user_id)

    if not progress:
        await message.answer("🔖 У вас пока нет завершённых модулей.")
        return

    response = "📊 Ваш прогресс:\n"
    for module in progress:
        response += f"✔️ {module['title']} (Завершено: {module['completed_at']})\n"

    await message.answer(response)


# Открытие выбранного модуля
@intern_router.callback_query(F.data.startswith("open_module_"))
async def open_module(callback: CallbackQuery, state: FSMContext):
    module_id = int(callback.data.split("_")[-1])
    lessons = await db.get_lessons_by_module(module_id)

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
            text="✅ Завершить", callback_data=f"finish_module_{module_id}"
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


# Завершение модуля
@intern_router.callback_query(F.data.startswith("finish_module_"))
async def finish_module(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    temporary_msgs = data.get("temporary_msgs", [])
    for msg_id in temporary_msgs:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)

    module_id = int(callback.data.split("_")[-1])

    # Получаем вопросы теста из БД
    questions = await db.get_test_questions(module_id)

    if not questions:
        # TODO: СЧИТАЕМ МОДУЛЬ ПРОЙДЕННЫМ
        await callback.message.answer(
            "❗ Для этого модуля тест ещё не создан.",
            reply_markup=get_intern_keyboard(),
        )
        return

    # Сохраняем вопросы в FSM
    await state.update_data(
        module_id=module_id,
        questions=questions,
        current_question_index=0,
        correct_answers=0,
    )
    await send_next_question(callback.message, state)


# Отправка следующего вопроса
async def send_next_question(message: Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions", [])
    current_index = data.get("current_question_index", 0)

    if current_index >= len(questions):
        await finish_test(message, state)
        return

    question = questions[current_index]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=question[f"option_{i}"], callback_data=f"answer_{i}"
                )
            ]
            for i in range(1, 5)
        ]
    )

    await message.answer(f"❓ {question['question']}", reply_markup=keyboard)


# Обработка ответа
@intern_router.callback_query(F.data.startswith("answer_"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions", [])
    current_index = data.get("current_question_index", 0)
    correct_answers = data.get("correct_answers", 0)

    question = questions[current_index]
    selected_option = int(callback.data.split("_")[-1])

    # Проверяем правильность ответа
    if selected_option == question["correct_option"]:
        correct_answers += 1

    # Сохраняем прогресс в FSM
    await state.update_data(
        current_question_index=current_index + 1, correct_answers=correct_answers
    )

    await send_next_question(callback.message, state)


async def finish_test(message: Message, state: FSMContext):
    data = await state.get_data()
    module_id = data.get("module_id")
    correct_answers = data.get("correct_answers", 0)
    total_questions = len(data.get("questions", []))

    # Проверка прохождения теста
    if (
        correct_answers / total_questions >= 0.7
    ):  # Успешное прохождение: 70% правильных ответов
        await db.update_module_progress(
            user_id=message.from_user.id, module_id=module_id, is_completed=True
        )
        await message.answer(
            f"🎉 Вы успешно прошли тест модуля! Правильных ответов: {correct_answers} из {total_questions}.",
            reply_markup=get_intern_keyboard(),
        )
    else:
        await message.answer(
            f"❌ Тест не пройден. Правильных ответов: {correct_answers} из {total_questions}. Повторите модуль.",
            reply_markup=get_intern_keyboard(),
        )

    await state.clear()
