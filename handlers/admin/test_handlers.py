import db
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from contexts import TestCreationFSM, ModuleCreationFSM, FinalExamCreationFSM
from keyboards import (
    get_test_management_keyboard,
    get_back_keyboard,
    get_finish_test_keyboard,
    get_admin_keyboard,
    get_dangerous_accept_keyboard,
    get_final_exam_management_keyboard,
    get_final_exam_question_type_keyboard,
    get_finish_exam_test_keyboard,
)

admin_router = Router()

log = logging.getLogger(__name__)


# Управление тестом
@admin_router.callback_query(F.data.startswith("manage_test_"))
async def manage_test(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])
    await callback.message.answer(
        "Выберите действие для теста:",
        reply_markup=get_test_management_keyboard(module_id),
    )
    await callback.answer()


# Начало создания теста
@admin_router.callback_query(F.data.startswith("add_test_question_"))
async def start_test_creation(callback: CallbackQuery, state: FSMContext):
    module_id = int(callback.data.split("_")[-1])
    await state.update_data(module_id=module_id, questions=[])
    await callback.message.answer(
        "Введите текст первого вопроса:", reply_markup=get_back_keyboard()
    )
    await callback.answer()
    await state.set_state(TestCreationFSM.waiting_for_question)


# Ввод вопроса
@admin_router.message(TestCreationFSM.waiting_for_question)
async def add_question_text(message: Message, state: FSMContext):
    await state.update_data(current_question=message.text.strip())
    await message.answer("Введите 4 варианта ответа (каждый с новой строки):")
    await state.set_state(TestCreationFSM.waiting_for_options)


# Ввод вариантов ответа
@admin_router.message(TestCreationFSM.waiting_for_options)
async def add_options(message: Message, state: FSMContext):
    options = message.text.strip().split("\n")
    if len(options) != 4:
        await message.answer("Должно быть 4 варианта ответа. Попробуйте снова.")
        return

    await state.update_data(current_options=options)
    await message.answer("Какой вариант правильный? Введите номер (1-4):")
    await state.set_state(TestCreationFSM.waiting_for_correct_option)


# Ввод правильного ответа
@admin_router.message(TestCreationFSM.waiting_for_correct_option)
async def add_correct_option(message: Message, state: FSMContext):
    try:
        correct_option = int(message.text.strip())
        if correct_option not in [1, 2, 3, 4]:
            raise ValueError
    except ValueError:
        await message.answer("Введите номер правильного ответа (1-4).")
        return

    data = await state.get_data()
    module_id = data.get("module_id")
    question = data.get("current_question")
    options = data.get("current_options")

    # Сохранение вопроса в БД
    await db.add_question_to_test(module_id, question, options, correct_option)

    await message.answer(
        "Вопрос добавлен. Хотите завершить создание теста или добавить ещё один вопрос?",
        reply_markup=get_finish_test_keyboard(),
    )
    data = await state.get_data()

    in_module_creation = data.get("in_module_creation", False)
    if in_module_creation:
        await state.set_state(ModuleCreationFSM.waiting_for_test_creation)
    else:
        await state.set_state(TestCreationFSM.waiting_for_next_action)
        await state.update_data(module_title=f"#{module_id}")


# Завершение создания теста
@admin_router.callback_query(
    F.data == "finish_test_creation", ModuleCreationFSM.waiting_for_test_creation
)
async def finish_test_creation_on_module(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    module_title = data.get("module_title")

    await callback.message.answer(
        f"📚 Модуль '{module_title}' успешно создан вместе с тестом!",
        reply_markup=get_admin_keyboard(),
    )
    await state.clear()
    await callback.answer()


# Завершение создания теста
@admin_router.callback_query(
    F.data == "finish_test_creation", TestCreationFSM.waiting_for_next_action
)
async def finish_test_creation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    module_title = data.get("module_title")

    await callback.message.answer(
        f"📚 Тест для модуля '{module_title}' успешно создан!",
        reply_markup=get_admin_keyboard(),
    )
    await state.clear()
    await callback.answer()


# Добавление ещё одного вопроса
@admin_router.callback_query(F.data == "add_another_question")
async def add_another_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст следующего вопроса:")
    await callback.answer()
    await state.set_state(TestCreationFSM.waiting_for_question)


# Удаление теста
@admin_router.callback_query(F.data.startswith("delete_test_"))
async def confirm_delete_test(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])
    await callback.message.answer(
        "❗ Вы уверены, что хотите удалить тест для этого модуля?",
        reply_markup=get_dangerous_accept_keyboard(action=f"delete_test_{module_id}"),
    )
    await callback.answer()


# Подтверждение удаления теста
@admin_router.callback_query(F.data.startswith("accept_delete_test_"))
async def delete_test_handler(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])
    log.info(
        f"Пользователь {callback.message.from_user.id} удалил тест к модулю #{module_id}"
    )
    # Удаляем тест из базы данных
    await db.delete_test(module_id)

    await callback.message.answer("❌ Тест для этого модуля успешно удалён.")
    await callback.answer()


# Отмена удаления теста
@admin_router.callback_query(F.data.startswith("cancel_delete_test_"))
async def cancel_delete_test(callback: CallbackQuery):
    await callback.message.answer("Удаление теста отменено.")
    await callback.answer()


# Просмотр теста
@admin_router.callback_query(F.data.startswith("view_test_"))
async def view_test_handler(callback: CallbackQuery):
    module_id = int(callback.data.split("_")[-1])

    # Получаем список вопросов из базы данных
    questions = await db.get_test_questions(module_id)

    if not questions:
        await callback.message.answer("❗ Тест для этого модуля ещё не создан.")
        return

    # Формируем сообщение с вопросами
    response = "📋 Вопросы теста:\n\n"
    for idx, question in enumerate(questions, start=1):
        response += f"{idx}. {question['question']}\n"
        response += f"  1️⃣ {question['option_1']}\n"
        response += f"  2️⃣ {question['option_2']}\n"
        response += f"  3️⃣ {question['option_3']}\n"
        response += f"  4️⃣ {question['option_4']}\n"
        response += f"✅ Правильный ответ: {question['correct_option']}\n\n"

    await callback.message.answer(response)
    await callback.answer()


# Управление финальной аттестацией
@admin_router.callback_query(F.data == "manage_final_exam")
async def manage_final_exam(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите действие для финальной аттестации:",
        reply_markup=get_final_exam_management_keyboard(),
    )
    await callback.answer()


# Добавление вопроса в финальную аттестацию
@admin_router.callback_query(F.data == "add_final_exam_question")
async def start_final_exam_creation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст вопроса:")
    await callback.answer()
    await state.clear()
    await state.set_state(FinalExamCreationFSM.waiting_for_question)


# Ввод вопроса
@admin_router.message(FinalExamCreationFSM.waiting_for_question)
async def get_final_exam_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text.strip())
    await message.answer(
        "Этот вопрос с вариантами ответов?",
        reply_markup=get_final_exam_question_type_keyboard(),
    )
    await state.set_state(FinalExamCreationFSM.waiting_for_question_type)


# Определение типа вопроса
@admin_router.message(FinalExamCreationFSM.waiting_for_question_type)
async def get_final_exam_question_type(message: Message, state: FSMContext):
    is_open_question = True if message.text == "✏️ Нет" else False
    await state.update_data(is_open_question=is_open_question)

    if not is_open_question:
        await message.answer("Введите 4 варианта ответа (каждый с новой строки):")
        await state.set_state(FinalExamCreationFSM.waiting_for_options)
    else:
        await save_final_exam_question(message, state)


# Ввод вариантов ответа
@admin_router.message(FinalExamCreationFSM.waiting_for_options)
async def get_final_exam_options(message: Message, state: FSMContext):
    options = message.text.strip().split("\n")
    if len(options) != 4:
        await message.answer("Должно быть 4 варианта ответа. Попробуйте снова.")
        return

    await state.update_data(options=options)
    await message.answer("Какой вариант правильный? Введите номер (1-4):")
    await state.set_state(FinalExamCreationFSM.waiting_for_correct_option)


# Ввод правильного ответа
@admin_router.message(FinalExamCreationFSM.waiting_for_correct_option)
async def get_final_exam_correct_option(message: Message, state: FSMContext):
    try:
        correct_option = int(message.text.strip())
        if correct_option not in [1, 2, 3, 4]:
            raise ValueError
    except ValueError:
        await message.answer("Введите номер правильного ответа (1-4).")
        return

    await state.update_data(correct_option=correct_option)
    await save_final_exam_question(message, state)


# Сохранение вопроса в БД
async def save_final_exam_question(message: Message, state: FSMContext):
    data = await state.get_data()
    question = data.get("question")
    is_open_question = data.get("is_open_question")
    options = data.get("options", [])
    correct_option = data.get("correct_option")

    await db.add_final_exam_question(
        question, is_open_question, options, correct_option
    )

    await message.answer(
        "Вопрос успешно добавлен! Хотите добавить ещё один или завершить?",
        reply_markup=get_finish_exam_test_keyboard(),
    )
    await state.set_state(FinalExamCreationFSM.waiting_for_next_action)


# Завершение создания теста
@admin_router.callback_query(F.data == "finish_exam_creation")
async def finish_final_exam_creation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Финальная аттестация успешно сохранена!", reply_markup=get_admin_keyboard()
    )
    await state.clear()
    await callback.answer()


# Просмотр вопросов аттестации
@admin_router.callback_query(F.data == "view_final_exam_questions")
async def view_final_exam_questions(callback: CallbackQuery):
    questions = await db.get_final_exam_questions()

    if not questions:
        await callback.message.answer(
            "❗ Вопросы финальной аттестации ещё не добавлены."
        )
        await callback.answer()
        return

    response = "📋 Вопросы финальной аттестации:\n\n"
    for idx, question in enumerate(questions, start=1):
        response += f"{idx}. {question['question']}\n"
        if not question["is_open_question"]:
            response += f"  1️⃣ {question['option_1']}\n"
            response += f"  2️⃣ {question['option_2']}\n"
            response += f"  3️⃣ {question['option_3']}\n"
            response += f"  4️⃣ {question['option_4']}\n"
            response += f"✅ Правильный ответ: {question['correct_option']}\n\n"

    await callback.message.answer(response)
    await callback.answer()
