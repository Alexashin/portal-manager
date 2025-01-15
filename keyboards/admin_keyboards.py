from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура для выбора действия после добавления урока
def get_add_new_lesson_keyboard_markup():
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить урок", callback_data="add_lesson")],
        [InlineKeyboardButton(text="✅ Завершить модуль", callback_data="finish_module")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

