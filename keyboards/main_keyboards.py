from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Управление обучением")],
            [KeyboardButton(text="👥 Пользователи"), KeyboardButton(text="📊 Статистика")]
        ],
        resize_keyboard=True
    )

def get_intern_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Доступные модули")],
            [KeyboardButton(text="📝 Моя статистика")]
        ],
        resize_keyboard=True
    )

def get_employee_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Материалы")],
            [KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

def get_back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )