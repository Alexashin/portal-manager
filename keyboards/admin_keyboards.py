from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inline-клавиатура для управления обучением
def get_training_management_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать новый модуль", callback_data="create_new_module")],
        [InlineKeyboardButton(text="📋 Список модулей", callback_data="list_modules")]
    ])

# Клавиатура для управления уроками в модуле
def get_add_new_lesson_keyboard_markup():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить урок", callback_data="add_lesson")],
        [InlineKeyboardButton(text="✅ Завершить модуль", callback_data="finish_module")]
    ])
    return keyboard

# Клавиатура для действий с уроком (пропустить или загрузить файл)
def get_skip_or_upload_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📎 Загрузить файл", callback_data="upload_file")],
        [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_step")]
    ])
    return keyboard
