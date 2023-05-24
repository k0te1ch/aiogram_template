from aiogram.types import ReplyKeyboardMarkup

from bot import context


class ru:
    lang = "ru"

    cancel = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel.add(context[lang].cancel)


class en:
    lang = "en"

    cancel = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel.add(context[lang].cancel)