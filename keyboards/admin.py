from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services import context


def admin_main_kb(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, data in context[language].admin_panel_main:
        builder.button(text=text, callback_data=data)
    builder.adjust(1)
    return builder.as_markup()


def bot_commands_kb(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, data in context[language].bot_commands:
        builder.button(text=text, callback_data=data)
    builder.button(text=context[language].back, callback_data="back")
    builder.adjust(1)
    return builder.as_markup()
