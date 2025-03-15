from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from typing import Dict, Any


def get_avaible_modules_keyboard(modules: Dict[str, Any]) -> InlineKeyboardMarkup:
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


def get_exam_answers_keyboard(question_data: Dict[str, Any]) -> InlineKeyboardMarkup:
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
