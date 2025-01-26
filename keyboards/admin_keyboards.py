from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Inline-клавиатура для управления обучением
def get_training_management_inline_keyboard() -> ReplyKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать новый модуль", callback_data="create_new_module")],
        [InlineKeyboardButton(text="📋 Список модулей", callback_data="list_modules")]
    ])


# Клавиатура для управления уроками в модуле
def get_add_new_lesson_keyboard_markup() -> ReplyKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить урок", callback_data="add_lesson")],
        [InlineKeyboardButton(text="✅ Завершить модуль", callback_data="finish_module")]
    ])
    return keyboard


# Клавиатура для действий с уроком (пропустить или загрузить файл)
def get_skip_or_upload_keyboard() -> ReplyKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📎 Загрузить файл", callback_data="upload_file")],
        [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_step")]
    ])
    return keyboard


# Клавиатура для управления модулем
def get_module_management_keyboard(module_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редактировать модуль", callback_data=f"edit_module_title_and_desc_{module_id}")],
            [InlineKeyboardButton(text="📖 Управление уроками", callback_data=f"manage_lessons_{module_id}")],
            [InlineKeyboardButton(text="🧪 Управление тестом", callback_data=f"manage_test_{module_id}")],
            [InlineKeyboardButton(text="🗑 Удалить модуль", callback_data=f"delete_module_{module_id}")]
        ]
    )


# Клавиатура для вывода списка модулей
def get_modules_admin_keyboard(modules) -> ReplyKeyboardMarkup:
    keyboard = [
            [InlineKeyboardButton(text=module['title'], callback_data=f"admin_view_module_{module['id']}")]
            for module in modules
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для управления уроками в модуле
def get_lessons_management_keyboard(module_id, lessons) -> ReplyKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=f"📖 {lesson['title']}", callback_data=f"view_lesson_{lesson['id']}")]
        for lesson in lessons
    ]
    keyboard.append([InlineKeyboardButton(text="➕ Добавить урок", callback_data=f"add_lesson_{module_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для управления конкретным уроком
def get_lesson_management_keyboard(lesson_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать урок", callback_data=f"edit_lesson_{lesson_id}")],
        [InlineKeyboardButton(text="🗑 Удалить урок", callback_data=f"delete_lesson_{lesson_id}")]
    ])


# Клавиатура для управления тестами
def get_test_management_keyboard(module_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить вопрос", callback_data=f"add_test_question_{module_id}")],
        [InlineKeyboardButton(text="📋 Просмотреть тест", callback_data=f"view_test_{module_id}")],
        [InlineKeyboardButton(text="❌ Удалить тест", callback_data=f"delete_test_{module_id}")]
    ])


# Клавиатура для завершения создания теста
def get_finish_test_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✔️ Завершить создание теста", callback_data="finish_test_creation")],
        [InlineKeyboardButton(text="➕ Добавить ещё один вопрос", callback_data="add_another_question")]
    ])