from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_avaible_modules_keyboard(modules: list):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=module["title"], callback_data=f"open_module_{module['id']}"
                )
            ]
            for module in modules
        ]
    )


def get_exam_answers_keyboard(question_data):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=question_data[f"option_{i}"], callback_data=f"exam_answer_{i}"
                )
            ]
            for i in range(1, 5)
        ]
    )
