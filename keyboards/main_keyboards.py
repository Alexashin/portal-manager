from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Управление обучением")],
            [
                KeyboardButton(text="👥 Пользователи"),
                KeyboardButton(text="📊 Статистика"),
            ],
        ],
        resize_keyboard=True,
    )


def get_intern_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Доступные модули")],
            [
                KeyboardButton(text="📊 Мой прогресс"),
                KeyboardButton(text="📝 Аттестация"),
            ],
        ],
        resize_keyboard=True,
    )


def get_start_exam_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Пройти аттестацию", callback_data="start_final_exam"
                )
            ]
        ]
    )


def get_employee_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Материалы")],
            [KeyboardButton(text="❓ Помощь")],
        ],
        resize_keyboard=True,
    )


def get_back_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад")]], resize_keyboard=True
    )


def get_dangerous_accept_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data=f"accept_{action}")],
            [InlineKeyboardButton(text="Нет", callback_data=f"cancel_{action}")],
        ],
        resize_keyboard=True,
    )
