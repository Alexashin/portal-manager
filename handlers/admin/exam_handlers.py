import db
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import (
    get_employee_keyboard,
    get_exam_attempts_keyboard,
    get_dangerous_accept_keyboard,
)
from create_bot import bot

admin_router = Router()


# Отклонение аттестации (повторное обучение)
@admin_router.callback_query(F.data.startswith("reject_exam_"))
async def reject_exam(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])

    # Отмечаем только ПОСЛЕДНЮЮ попытку как "не пройденную"
    await db.reject_last_exam_attempt(user_id)

    # Редактируем сообщение: удаляем кнопки и добавляем статус
    new_text = callback.message.text + "\n\n❌ <b>Аттестация отклонена</b>."
    await callback.message.edit_text(new_text)

    # Уведомляем пользователя о необходимости пересдачи
    try:
        await bot.send_message(
            user_id,
            "❌ Ваша аттестация не принята. Вам необходимо пройти обучение заново.",
        )
    except Exception:
        pass  # Если бот не может отправить сообщение, продолжаем работу

    await callback.answer("Аттестация отклонена ❌", show_alert=True)


# Подтверждение аттестации (перевод в сотрудника)
@admin_router.callback_query(F.data.startswith("approve_exam_"))
async def approve_exam(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])

    # Обновляем роль пользователя в БД
    await db.promote_to_employee(user_id)

    # Редактируем сообщение: удаляем кнопки и добавляем статус
    new_text = callback.message.text + "\n\n✅ <b>Аттестация принята</b>."
    await callback.message.edit_text(new_text)

    # Уведомляем пользователя о повышении
    try:
        await bot.send_message(
            user_id,
            "🎉 Поздравляем! Вы успешно прошли аттестацию и теперь являетесь сотрудником.",
            reply_markup=get_employee_keyboard(),
        )
    except Exception:
        pass  # Игнорируем ошибку отправки сообщения пользователю

    await callback.answer("Аттестация подтверждена ✅", show_alert=True)


# Просмотр истории аттестаций
@admin_router.callback_query(F.data.startswith("view_exam_history_"))
async def view_exam_history(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    attempts = await db.get_user_exam_attempts(user_id)

    if not attempts:
        await callback.message.answer("❗ У пользователя нет истории аттестаций.")
        return
    user_info = await db.get_employee_info(user_id)
    response = (
        f"📊 <b>История аттестаций пользователя {user_info['full_name']}:</b>\n\n"
    )
    for attempt in attempts:
        status = "✅ ПРОЙДЕН" if attempt["passed"] else "❌ НЕ ПРОЙДЕН"
        response += (
            f"📅 {attempt['attempt_date'].strftime('%d.%m.%Y')}\n"
            f"🔢 Попытка #{attempt['attempt_number']}\n"
            f"✔️ {attempt['correct_answers']} из {attempt['total_questions']} правильных\n"
            f"📊 Статус: {status}\n\n"
        )

    await callback.message.answer(
        response, reply_markup=get_exam_attempts_keyboard(user_id, attempts)
    )
    await callback.answer()


# Просмотр конкретной попытки аттестации
@admin_router.callback_query(F.data.startswith("view_exam_attempt_"))
async def view_exam_attempt(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id = int(parts[3])
    attempt_number = int(parts[4])

    answers = await db.get_exam_attempt_answers(user_id, attempt_number)

    if not answers:
        await callback.message.answer("❗ Нет данных по данной попытке.")
        return

    user_info = await db.get_employee_info(user_id)

    response = f"📋 <b>Ответы пользователя {user_info['full_name']}, попытка #{attempt_number}:</b>\n\n"
    for answer in answers:
        response += f"❓ {answer['question']}\n"
        if answer["open_answer"]:
            response += f"📝 Открытый ответ: {answer['open_answer']}\n\n"
        else:
            status = "✅" if answer["is_correct"] else "❌"
            response += (
                f"🔘 Выбранный ответ: {status} {answer['chosen_option_text']}\n\n"
            )

    await callback.message.answer(response)
    await callback.answer()


# Удаление финальной аттестации
@admin_router.callback_query(F.data == "delete_final_exam_questions")
async def confirm_delete_exam(callback: CallbackQuery):
    await callback.message.answer(
        "❗ Вы уверены, что хотите удалить всю финальную аттестацию?",
        reply_markup=get_dangerous_accept_keyboard(action="delete_final_exam"),
    )
    await callback.answer()


# Подтверждение удаления теста
@admin_router.callback_query(F.data == "accept_delete_final_exam")
async def delete_test_exam(callback: CallbackQuery):
    # Удаляем аттестацию из базы данных
    await db.delete_all_final_exam_questions()

    await callback.message.answer("❌ Аттестация успешно удалена.")
    await callback.answer()


# Отмена удаления аттестации
@admin_router.callback_query(F.data == "cancel_delete_final_exam")
async def cancel_delete_test(callback: CallbackQuery):
    await callback.message.answer("Удаление аттестации отменено.")
    await callback.answer()
