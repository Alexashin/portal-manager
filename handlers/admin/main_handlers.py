from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from filters import RoleFilter
from keyboards import (
    get_admin_keyboard,
    get_training_management_inline_keyboard,
    get_user_list_keyboard,
)
import db

admin_router = Router()


async def is_back(message: Message, state: FSMContext) -> bool:
    if message.text == "🔙 Назад":
        await back_to_main_menu(message, state)
        return True
    else:
        return False


# Обработчик кнопки "🔙 Назад"
@admin_router.message(RoleFilter("manager"), F.text == "🔙 Назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню.", reply_markup=get_admin_keyboard()
    )


# Обработчик кнопки "📚 Управление обучением"
@admin_router.message(RoleFilter("manager"), F.text == "📚 Управление обучением")
async def manage_training(message: Message):
    await message.answer(
        "Выберите действие:", reply_markup=get_training_management_inline_keyboard()
    )


# Обработчик кнопки "👥 Пользователи"
@admin_router.message(RoleFilter("manager"), F.text == "👥 Пользователи")
async def list_users(message: Message):
    users = await db.get_all_users()

    if not users:
        await message.answer("📌 В системе пока нет пользователей.")
        return

    await message.answer(
        "📋 Список пользователей:", reply_markup=get_user_list_keyboard(users)
    )


# Обработчик кнопки "📊 Статистика"
@admin_router.message(RoleFilter("manager"), F.text == "📊 Статистика")
async def view_statistics(message: Message):
    # Получаем данные из БД
    user_stats = await db.get_user_statistics()
    training_stats = await db.get_training_statistics()
    progress_stats = await db.get_progress_statistics()

    # Формируем сообщение со статистикой
    response = "📊 <b>Общая статистика:</b>\n\n"

    # Количество пользователей
    response += "👥 <b>Пользователи:</b>\n"
    response += f"  🔹 Менеджеров: {user_stats['managers']}\n"
    response += f"  🔹 Сотрудников: {user_stats['employees']}\n"
    response += f"  🔹 Стажёров: {user_stats['interns']}\n\n"

    # Количество модулей, уроков, тестов
    response += "📚 <b>Обучение:</b>\n"
    response += f"  🔸 Модулей: {training_stats['total_modules']}\n"
    response += f"  🔸 Уроков: {training_stats['total_lessons']}\n"
    response += f"  🔸 Тестов: {training_stats['total_tests']}\n"
    response += f"  🔸 Вопросов в финальной аттестации: {training_stats['total_exam_questions']}\n\n"

    # Статистика тестов и модулей
    response += "🎓 <b>Прогресс обучения:</b>\n"
    response += f"  ✅ Завершённых модулей: {progress_stats['completed_modules']}\n"
    avg_score = (
        round(progress_stats["avg_test_score"], 2)
        if progress_stats["avg_test_score"] is not None
        else 0
    )
    response += f"  📈 Средний процент правильных ответов в тестах: {avg_score}%"

    # Отправляем статистику администратору
    await message.answer(response)


# Команда для изменения настроек
@admin_router.message(RoleFilter("manager"), F.text.startswith("/set_setting"))
async def set_bot_setting(message: Message):
    parts = message.text.split(" ", 2)
    if len(parts) < 3:
        await message.answer("Используйте формат: /set_setting ключ значение")
        return

    setting_key, new_value = parts[1], parts[2]

    # Проверяем, что ключ существует в разрешённом списке
    allowed_settings = [
        "backup_frequency",
        "admin_notifications_id",
        "exam_pass_percentage",
    ]
    if setting_key not in allowed_settings:
        await message.answer("❌ Ошибка: данный параметр нельзя изменять!")
        return

    await db.update_bot_setting(setting_key, new_value)
    await message.answer(f"✅ Настройка `{setting_key}` обновлена на `{new_value}`.")
