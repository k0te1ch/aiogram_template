from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from services import context


def cancel_kb(language: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=context[language].cancel)
    return builder.as_markup(resize_keyboard=True)
