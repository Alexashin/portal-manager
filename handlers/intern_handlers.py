import db
import logging
from aiogram_run import bot
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from contexts import FinalExamFSM
from filters import RoleFilter

from keyboards import (
    get_intern_keyboard,
    get_avaible_modules_keyboard,
    get_start_exam_keyboard,
    get_back_keyboard,
    get_exam_answers_keyboard,
    get_exam_result_keyboard,
)

intern_router = Router()

log = logging.getLogger(__name__)


# Обработчик кнопки "🔙 Назад"
@intern_router.message(RoleFilter("intern"), F.text == "🔙 Назад")
async def back_to_main_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню.", reply_markup=get_intern_keyboard()
    )


@intern_router.message(RoleFilter("intern"), F.text == "📖 Доступные модули")
async def show_modules(message: Message) -> None:
    user_id = message.from_user.id

    # Проверяем доступные модули
    modules = await db.get_available_modules_for_user(user_id)

    # Если доступных модулей нет, открываем первый модуль
    if not modules:
        first_module = await db.get_first_module()
        if first_module:
            await db.make_module_accessible(user_id, first_module["id"])
            modules = [first_module]

    if not modules:
        await message.answer("❗ У вас пока нет доступных модулей.")
        return

    await message.answer(
        "📚 Ваши доступные модули:", reply_markup=get_avaible_modules_keyboard(modules)
    )


# Отображение прогресса
@intern_router.message(RoleFilter("intern"), F.text == "📊 Мой прогресс")
async def show_progress(message: Message) -> None:
    user_id = message.from_user.id
    progress = await db.get_user_progress(user_id)

    if not progress:
        await message.answer("🔖 У вас пока нет завершённых модулей.")
        return

    response = "📊 Ваш прогресс:\n"
    for module in progress:
        response += f"✔️ {module['title']} (Завершено: {module['completed_at']})\n"

    await message.answer(response)


# Проверка доступности аттестации
@intern_router.message(RoleFilter("intern"), F.text == "📝 Аттестация")
async def check_exam_availability(message: Message) -> None:
    user_id = message.from_user.id
    exam_access = await db.check_final_exam_access(user_id)

    if exam_access:
        await message.answer(
            "🎓 Вы завершили обучение! Теперь вы можете пройти итоговую аттестацию.",
            reply_markup=get_start_exam_keyboard(),
        )
    else:
        await message.answer("📚 Вам нужно завершить все модули перед аттестацией.")


# Открытие выбранного модуля
@intern_router.callback_query(RoleFilter("intern"), F.data.startswith("open_module_"))
async def open_module(callback: CallbackQuery, state: FSMContext) -> None:
    module_id = int(callback.data.split("_")[-1])
    lessons = await db.get_lessons_by_module(module_id)

    if not lessons:
        await callback.message.answer("❗ В этом модуле пока нет уроков.")
        return
    await state.update_data(module_id=module_id, lesson_index=0)
    await callback.message.edit_text("✅ Начато обучение!")
    data = await state.get_data()
    temporary_msgs = data.get("temporary_msgs", [])
    if temporary_msgs != []:
        for msg_id in temporary_msgs:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)
        await state.update_data(temporary_msgs=[])
    await send_lesson(callback.message, state, 0, module_id)
    await callback.answer()


@intern_router.callback_query(RoleFilter("intern"), F.data.startswith("open_lesson_"))
async def change_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    lesson_id = int(callback.data.split("_")[-1])
    module_id = int(callback.data.split("_")[-2])
    data = await state.get_data()
    temporary_msgs = data.get("temporary_msgs", [])
    if temporary_msgs != []:
        for msg_id in temporary_msgs:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)
        await state.update_data(temporary_msgs=[])
    await send_lesson(callback.message, state, lesson_id, module_id)
    await callback.answer()


# Отправка урока с навигацией
async def send_lesson(
    message: Message, state: FSMContext, index: int, module_id: int
) -> None:
    lessons = await db.get_lessons_by_module(module_id)
    lesson = lessons[index]
    total_lessons = len(lessons)

    text = f"<b>{lesson['title']}</b>\nФайлы урока:"

    buttons = list()
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
    msg = await message.answer(text, reply_markup=get_back_keyboard())
    new_temporary_msgs.append(msg.message_id)
    for file_id in lesson.get("file_ids", []):
        try:
            msg = await message.answer_document(file_id)
            new_temporary_msgs.append(msg.message_id)
        except Exception as ex:
            log.error(
                f"Ошибка отправки файла! Модуль #{module_id}; урок #{index}: {ex}"
            )
            await message.answer("Ошибка отправки файла!")

    for video_id in lesson.get("video_ids", []):
        try:
            msg = await message.answer_video(video_id)
            new_temporary_msgs.append(msg.message_id)
        except Exception as ex:
            log.error(
                f"Ошибка отправки видео! Модуль #{module_id}; урок #{index}: {ex}"
            )
            await message.answer("Ошибка отправки видео!")
    msg = await message.answer(f"{lesson['content']}")
    new_temporary_msgs.append(msg.message_id)
    msg = await message.answer("<b>Продолжим?</b>", reply_markup=keyboard)
    new_temporary_msgs.append(msg.message_id)
    await state.update_data(temporary_msgs=new_temporary_msgs)


# Завершение модуля
@intern_router.callback_query(RoleFilter("intern"), F.data.startswith("finish_module_"))
async def finish_module(callback: CallbackQuery, state: FSMContext) -> None:
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
        await callback.answer()
        return

    # Сохраняем вопросы в FSM
    await state.update_data(
        module_id=module_id,
        questions=questions,
        current_question_index=0,
        correct_answers=0,
    )
    await send_next_question(callback.message, state)
    await callback.answer()


# Отправка следующего вопроса
async def send_next_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    temp_test_msg = data.get("temp_test_msg", None)
    if temp_test_msg is not None:
        await bot.delete_message(chat_id=message.chat.id, message_id=temp_test_msg)
        await state.update_data(temporary_msgs=None)
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

    msg = await message.answer(f"❓ {question['question']}", reply_markup=keyboard)
    await state.update_data(temp_test_msg=msg.message_id)


# Обработка ответа
@intern_router.callback_query(RoleFilter("intern"), F.data.startswith("answer_"))
async def handle_answer(callback: CallbackQuery, state: FSMContext) -> None:
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
    await callback.answer()


async def finish_test(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    module_id = data.get("module_id")
    correct_answers = data.get("correct_answers", 0)
    total_questions = len(data.get("questions", []))

    # Проверка прохождения теста
    if correct_answers / total_questions * 100 >= int(
        await db.get_bot_setting("exam_pass_percentage") or 70
    ):  # Успешное прохождение: 70% правильных ответов
        await db.update_module_progress(
            user_id=message.chat.id, module_id=module_id, is_completed=True
        )

        # Делаем следующий модуль доступным
        next_module_id = await db.get_next_module_id(module_id)
        if next_module_id:
            await db.make_module_accessible(message.chat.id, next_module_id)
            await message.answer(
                f"🎉 Вы успешно прошли тест модуля! Правильных ответов: {correct_answers} из {total_questions}.\n"
                f"🔓 Доступ к следующему модулю открыт!",
                reply_markup=get_intern_keyboard(),
            )
            log.info(
                f"Пользователь {message.chat.id} открыл доступ к модулю {next_module_id}."
            )
        else:
            await message.answer(
                f"🎉 Вы успешно прошли тест модуля! Правильных ответов: {correct_answers} из {total_questions}.\n"
                f"✅ Это был последний модуль!",
                reply_markup=get_intern_keyboard(),
            )
            log.info(f"Пользователь {message.chat.id} завершил обучение.")
    else:
        await message.answer(
            f"❌ Тест не пройден. Правильных ответов: {correct_answers} из {total_questions}.\n"
            f"🔁 Повторите модуль и попробуйте снова.",
            reply_markup=get_intern_keyboard(),
        )

    await state.clear()


# Начало аттестации
@intern_router.callback_query(RoleFilter("intern"), F.data == "start_final_exam")
async def start_final_exam(callback: CallbackQuery, state: FSMContext) -> None:
    questions = await db.get_final_exam_questions()

    if not questions:
        await callback.message.answer(
            "❗ В системе пока нет доступных вопросов для аттестации."
        )
        await callback.answer()
        return

    await state.update_data(exam_questions=questions, current_question=0, answers=[])

    await callback.message.answer(
        "📝 Начинаем итоговую аттестацию!", reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()
    await send_next_exam_question(callback.message, state)


# Отправка следующего вопроса
async def send_next_exam_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    temp_test_msg = data.get("temp_test_msg", None)
    if temp_test_msg is not None:
        await bot.delete_message(chat_id=message.chat.id, message_id=temp_test_msg)
        await state.update_data(temporary_msgs=None)
    questions = data.get("exam_questions", [])
    current_index = data.get("current_question", 0)

    if current_index >= len(questions):
        await finish_final_exam(message, state)
        return

    question = questions[current_index]
    question_text = f"❓ {question['question']}"

    if question["is_open_question"]:
        msg = await message.answer(f"{question_text}\nВведите текстовый ответ:")
        await state.set_state(FinalExamFSM.waiting_for_open_answer)
    else:
        msg = await message.answer(
            question_text, reply_markup=get_exam_answers_keyboard(question)
        )

    await state.update_data(current_question=current_index + 1)
    await state.update_data(temp_test_msg=msg.message_id)


# Обработка тестовых ответов аттестации
@intern_router.callback_query(RoleFilter("intern"), F.data.startswith("exam_answer_"))
async def handle_exam_answer(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data.get("exam_questions", [])
    current_index = data.get("current_question", 0)
    answers = data.get("answers", [])

    if current_index == 0 or current_index > len(questions):
        await callback.answer()
        return  # Ошибочный индекс вопроса

    question = questions[current_index - 1]
    selected_option = int(callback.data.split("_")[-1])

    is_correct = selected_option == question["correct_option"]
    answers.append(
        {
            "question_id": question["id"],
            "chosen_option": selected_option,
            "open_answer": None,  # Открытые вопросы отдельно
            "is_correct": is_correct,
        }
    )

    await state.update_data(answers=answers)
    await send_next_exam_question(callback.message, state)
    await callback.answer()


# Обработка текстовых ответов на открытые вопросы
@intern_router.message(RoleFilter("intern"), FinalExamFSM.waiting_for_open_answer)
async def handle_open_exam_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data.get("exam_questions", [])
    current_index = data.get("current_question", 0)
    answers = data.get("answers", [])

    if current_index == 0 or current_index > len(questions):
        return  # Нет активного вопроса

    question = questions[current_index - 1]  # Берём предыдущий вопрос

    # Записываем ответ пользователя
    user_answer = message.text.strip()
    answers.append(
        {
            "question_id": question["id"],
            "chosen_option": None,  # NULL, так как это открытый вопрос
            "open_answer": user_answer,
            "is_correct": None,  # Открытые вопросы проверяет админ
        }
    )

    await state.update_data(answers=answers)

    # Переходим к следующему вопросу
    await send_next_exam_question(message, state)


# Завершение аттестации
async def finish_final_exam(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = message.from_user.id
    answers = data.get("answers", [])

    if not answers:
        await message.answer("❌ Ошибка: не найдены ответы на вопросы.")
        return

    # Фильтруем тестовые вопросы (у них есть chosen_option) и открытые вопросы (у них есть open_answer)
    test_answers = [ans for ans in answers if ans.get("chosen_option") is not None]
    open_answers = [ans for ans in answers if ans.get("open_answer") is not None]

    correct_test_answers = sum(
        1 for answer in test_answers if answer.get("is_correct") is True
    )
    total_test_questions = len(test_answers)

    # Проверка успешного прохождения (ТОЛЬКО для тестовой части)
    passed = (
        correct_test_answers / total_test_questions * 100
        >= int(await db.get_bot_setting("exam_pass_percentage") or 70)
        if total_test_questions > 0
        else False
    )

    attempt_number = await db.get_next_attempt_number(user_id)
    # Сохраняем результат аттестации в `final_exam_results`
    await db.save_exam_result(
        user_id, total_test_questions, correct_test_answers, passed, attempt_number
    )

    # Сохраняем ответы в `final_exam_answers`
    await db.save_exam_answers(user_id, answers, attempt_number)

    # Отправляем уведомление администратору
    await notify_admin_about_exam(
        user_id, correct_test_answers, total_test_questions, passed
    )

    # Очистка состояния FSM
    await state.clear()

    if passed:
        await message.answer(
            f"🎉 Вы успешно прошли аттестацию!\n"
            f"✔️ {correct_test_answers}/{total_test_questions} правильных тестовых ответов.",
            reply_markup=get_intern_keyboard(),
        )
    else:
        await message.answer(
            f"❌ Аттестация не пройдена. ({correct_test_answers}/{total_test_questions})\n"
            f"Попробуйте снова.",
            reply_markup=get_intern_keyboard(),
        )


# Отправка уведомления администратору
async def notify_admin_about_exam(
    user_id: int,
    correct_test_answers: int,
    total_test_questions: int,
    passed: bool,
) -> None:
    admin_id = await db.get_bot_setting("admin_notifications_id")
    user_info = await db.get_employee_info(user_id)
    if not admin_id:
        return  # Если админ не найден, ничего не делаем

    # Получаем номер текущей попытки
    attempt_number = (
        int(await db.get_next_attempt_number(user_id)) - 1
    )  # -1, так как попытка уже сохранена

    result_text = (
        "✅ Тестовая часть пройдена" if passed else "❌ Тестовая часть не пройдена"
    )

    answers = await db.get_exam_attempt_answers(user_id, attempt_number)

    # Формируем текст с ответами
    answers_text = f"\n\n📋 <b>Ответы пользователя {user_info['full_name']}, попытка #{attempt_number}:</b>\n\n"
    for answer in answers:
        answers_text += f"❓ {answer['question']}\n"
        if answer["open_answer"]:
            answers_text += f"📝 Открытый ответ: {answer['open_answer']}\n\n"
        else:
            status = "✅" if answer["is_correct"] else "❌"
            answers_text += (
                f"🔘 Выбранный ответ: {status} {answer['chosen_option_text']}\n\n"
            )

    message_text = (
        f"📊 <b>Стажёр {user_info['full_name']} завершил аттестацию!</b>\n"
        f"✔️ {correct_test_answers} / {total_test_questions} правильных тестовых ответов\n"
        f"{result_text}"
        f"{answers_text}"
    )

    kb = get_exam_result_keyboard(user_id)

    # Отправка сообщения админу
    await bot.send_message(admin_id, message_text, reply_markup=kb)
