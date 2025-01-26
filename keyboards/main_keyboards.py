from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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
            [KeyboardButton(text="📊 Мой прогресс")]
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

def get_dangerous_accept_keyboard(action: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data=f"accept_{action}")],
            [InlineKeyboardButton(text="Нет", callback_data=f"cancel_{action}")]
        ],
        resize_keyboard=True
    )