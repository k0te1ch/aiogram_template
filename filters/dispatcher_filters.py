from aiogram.enums import ChatType
from aiogram.types import Message

from config import ADMINS, LANGUAGES
from filters.chat_type import ChatTypeFilter
from services import context


async def IsGroup(m) -> bool:
    """Whether the chat is a group or supergroup."""
    c = ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP])
    return await c(m)


async def IsPrivate(m) -> bool:
    """Whether the chat is private."""
    c = ChatTypeFilter(ChatType.PRIVATE)
    return await c(m)


async def IsChannel(m) -> bool:
    """Whether the chat is a channel."""
    c = ChatTypeFilter(ChatType.CHANNEL)
    return await c(m)


def IsAdmin(m) -> bool:
    """Whether the user's username is in the configured ADMINS list."""
    return m.from_user.username in ADMINS


def ContextButton(context_key: str | list, classes: list = LANGUAGES):
    """Match a message whose text equals a localized string (in any language).

    Example: ``ContextButton("cancel")`` matches the "Cancel"/"Отмена" buttons.
    """
    keys = [context_key] if isinstance(context_key, str) else context_key

    def inner(m) -> bool | None:
        if not (isinstance(m, Message) and m.text):
            return None
        for cls in classes:
            for key in keys:
                attr = getattr(context[cls], key)
                values = attr if isinstance(attr, list) else [attr]
                if m.text in values:
                    return True
        return None

    return inner
