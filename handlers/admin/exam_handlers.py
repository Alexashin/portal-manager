from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards import *
import db
from create_bot import bot

admin_router = Router()


# # Просмотр результатов аттестации
# @admin_router.callback_query(F.data.startswith("view_exam_results_"))
# async def view_exam_results(callback: CallbackQuery):
#     user_id = int(callback.data.split("_")[-1])
#     results = await db.get_exam_results(user_id)

#     if not results:
#         await callback.message.answer(
#             "❗ Нет данных по аттестации данного пользователя."
#         )
#         return

#     correct_count = sum(1 for res in results if res["is_correct"])
#     total_questions = len(results)
#     accuracy = round((correct_count / total_questions) * 100, 2)
#     user_info = await db.get_employee_info(user_id)
#     response = f"📊 **Результаты аттестации для пользователя {user_info['full_name']}:**\n\n"
#     response += (
#         f"✔️ Правильных ответов: {correct_count} / {total_questions} ({accuracy}%)\n\n"
#     )
#     response += "📋 **Ответы пользователя:**\n"

#     for idx, res in enumerate(results, 1):
#         response += f"\n❓ {res['question']}\n"
#         response += f"✅ Правильный ответ: {res[f'option_{res['correct_option']}']}\n"
#         response += (
#             f"🔘 Ответ пользователя: {res[f'option_{res['selected_option']}']}\n"
#         )

#     await callback.message.answer(response)


# Отклонение аттестации (повторное обучение)
@admin_router.callback_query(F.data.startswith("reject_exam_"))
async def reject_exam(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])

    # Удаляем результаты аттестации
    await db.reset_exam_attempt(user_id)
    user_info = await db.get_employee_info(user_id)
    await callback.message.answer(
        f"❌ Аттестация пользователя {user_info['full_name']} отклонена. Стажёру необходимо пройти обучение заново."
    )

    # Уведомляем пользователя о необходимости повторного обучения
    try:
        await bot.send_message(
            user_id,
            "❌ Ваша аттестация не принята. Вам необходимо пройти обучение заново.",
        )
    except Exception:
        pass  # Если бот не может отправить сообщение, продолжаем работу


# Подтверждение аттестации (перевод в сотрудника)
@admin_router.callback_query(F.data.startswith("approve_exam_"))
async def approve_exam(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])

    # Обновляем роль пользователя в БД
    await db.promote_to_employee(user_id)
    user_info = await db.get_employee_info(user_id)
    await callback.message.answer(
        f"✅ Пользователь {user_info['full_name']} успешно прошёл аттестацию и теперь является сотрудником."
    )

    # Уведомляем пользователя о повышении
    try:
        await bot.send_message(
            user_id,
            "🎉 Поздравляем! Вы успешно прошли аттестацию и теперь являетесь сотрудником.",
        )
    except Exception:
        pass  # Игнорируем ошибку отправки сообщения пользователю


# Удаление финальной аттестации
@admin_router.callback_query(F.data == "delete_final_exam_questions")
async def confirm_delete_exam(callback: CallbackQuery):
    await callback.message.answer(
        "❗ Вы уверены, что хотите удалить всю финальную аттестацию?",
        reply_markup=get_dangerous_accept_keyboard(action=f"delete_final_exam"),
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
