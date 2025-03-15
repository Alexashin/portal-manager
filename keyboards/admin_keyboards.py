from typing import Dict, Any
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from datetime import datetime as dt


# Inline-клавиатура для управления обучением
def get_training_management_inline_keyboard() -> InlineKeyboardButton:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Создать новый модуль", callback_data="create_new_module"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Список модулей", callback_data="list_modules"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Управление итоговой аттестацией",
                    callback_data="manage_final_exam",
                )
            ],
        ]
    )


# Клавиатура для управления уроками в модуле
def get_add_new_lesson_keyboard_markup() -> InlineKeyboardButton:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить урок", callback_data="add_lesson")],
            [
                InlineKeyboardButton(
                    text="✅ Завершить модуль", callback_data="finish_module"
                )
            ],
        ]
    )
    return keyboard


# Клавиатура для управления модулем
def get_module_management_keyboard(module_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать модуль",
                    callback_data=f"edit_module_title_and_desc_{module_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📖 Управление уроками",
                    callback_data=f"manage_lessons_{module_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧪 Управление тестом",
                    callback_data=f"manage_test_{module_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить модуль", callback_data=f"delete_module_{module_id}"
                )
            ],
        ]
    )


# Клавиатура для вывода списка модулей
def get_modules_admin_keyboard(modules: Dict[str, Any]) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=module["title"], callback_data=f"admin_view_module_{module['id']}"
            )
        ]
        for module in modules
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для управления уроками в модуле
def get_lessons_management_keyboard(
    module_id: int, lessons: Dict[str, Any]
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"📖 {lesson['title']}",
                callback_data=f"view_lesson_{lesson['id']}",
            )
        ]
        for lesson in lessons
    ]
    keyboard.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить урок", callback_data=f"add_lesson_{module_id}"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для управления конкретным уроком
def get_lesson_management_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать урок",
                    callback_data=f"edit_lesson_{lesson_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить урок", callback_data=f"delete_lesson_{lesson_id}"
                )
            ],
        ]
    )


# Клавиатура для управления тестами
def get_test_management_keyboard(module_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить вопрос",
                    callback_data=f"add_test_question_{module_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Просмотреть тест", callback_data=f"view_test_{module_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удалить тест", callback_data=f"delete_test_{module_id}"
                )
            ],
        ]
    )


# Клавиатура для завершения создания теста
def get_finish_test_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✔️ Завершить создание теста",
                    callback_data="finish_test_creation",
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Добавить ещё один вопрос",
                    callback_data="add_another_question",
                )
            ],
        ]
    )


# Клавиатура для завершения создания теста
def get_finish_exam_test_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✔️ Завершить создание теста",
                    callback_data="finish_exam_creation",
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Добавить ещё один вопрос",
                    callback_data="add_final_exam_question",
                )
            ],
        ]
    )


# Клавиатура для управления финальной аттестацией
def get_final_exam_management_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить вопрос", callback_data="add_final_exam_question"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Просмотреть вопросы",
                    callback_data="view_final_exam_questions",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удалить все вопросы",
                    callback_data="delete_final_exam_questions",
                )
            ],
        ]
    )


def get_final_exam_question_type_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✔️ Да"), KeyboardButton(text="✏️ Нет")]],
        resize_keyboard=True,
    )


def get_exam_result_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отклонить", callback_data=f"reject_exam_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить", callback_data=f"approve_exam_{user_id}"
                )
            ],
        ]
    )


def get_user_list_keyboard(users: Dict[str, Any]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{user['full_name']} ({user['role']})",
                    callback_data=f"view_user_{user['tg_id']}",
                )
            ]
            for user in users
        ]
    )
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить пользователя", callback_data="add_user"
            )
        ]
    )
    return keyboard


def get_user_managment_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏ Изменить роль", callback_data=f"change_role_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить", callback_data=f"delete_employee_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 История аттестаций",
                    callback_data=f"view_exam_history_{user_id}",
                )
            ],
        ]
    )


def get_exam_attempts_keyboard(user_id: int, attempts: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Попытка #{attempt['attempt_number']} ({dt.strftime(attempt['attempt_date'], '%d.%m.%Y')})",
                    callback_data=f"view_exam_attempt_{user_id}_{attempt['attempt_number']}",
                )
            ]
            for attempt in attempts
        ]
    )


def get_user_role_managment_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Стажёр", callback_data=f"set_role_intern_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👨‍💼 Сотрудник", callback_data=f"set_role_employee_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Менеджер", callback_data=f"set_role_manager_{user_id}"
                )
            ],
        ]
    )


def get_user_role_selector_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Стажёр", callback_data="set_role_intern")],
            [
                InlineKeyboardButton(
                    text="👨‍💼 Сотрудник", callback_data="set_role_employee"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Менеджер", callback_data="set_role_manager"
                )
            ],
        ]
    )
