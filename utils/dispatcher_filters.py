from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType, Message

from bot import context
from config import ADMINS, LANGUAGES


def IsGroup(m):
    """
    This filter checks whether the chat is group or super group
    :return: bool
    """
    return ChatTypeFilter([ChatType.GROUP, ChatType.SUPER_GROUP])


def IsPrivate(m):
    """
    This filter checks whether the chat is private
    :return: bool
    """
    return ChatTypeFilter(ChatType.PRIVATE)


def IsChannel(m):
    """
    This filter checks whether the chat is a channel
    :return: bool
    """
    return ChatTypeFilter(ChatType.CHANNEL)


def IsAdmin(m):
    """
    This filter checks whether the user is an administrator (in the list of administrators in the settings)
    :return: bool
    """
    return (m.from_user.id in ADMINS)


def ContextButton(context_key: str, classes: list = LANGUAGES):
    """
    This filter checks button's text when have a multi-language context
    example: ContextButton("cancel", ["ru", "en"])
    """
    def inner(m):
        if not(isinstance(m, Message) and m.text):
            return

        for cls in classes:
            if m.text == getattr(context[cls], context_key):
                return True
    return inner
