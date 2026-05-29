from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User
from loguru import logger

from config import LANGUAGES

EventType = TypeVar("EventType", bound=TelegramObject)


class UserContextMiddleware(BaseMiddleware):
    """Injects ``language`` and/or ``username`` into handlers that ask for them.

    Supports Message and CallbackQuery. A handler opts in simply by declaring
    a ``language`` or ``username`` parameter in its signature.
    """

    async def get_user(self, event: Message | CallbackQuery) -> User:
        if isinstance(event, (Message, CallbackQuery)):
            return event.from_user
        raise ValueError(f"Unsupported event type: {type(event)}")

    async def get_language(self, user: User) -> str:
        language = user.language_code if user.language_code in LANGUAGES else "ru"
        logger.trace(f"Resolved language {language} for user {user.id}")
        return language

    async def __call__(
        self,
        handler: Callable[[EventType, dict[str, Any]], Awaitable[Any]],
        event: EventType,
        data: dict[str, Any],
    ) -> Any:
        handler_info = data.get("handler")
        handler_params = getattr(handler_info, "params", set()) if handler_info else set()

        try:
            user = await self.get_user(event)
        except Exception as e:
            logger.warning(f"Could not extract user: {e}")
            return await handler(event, data)

        if "language" in handler_params:
            data["language"] = await self.get_language(user)

        if "username" in handler_params:
            data["username"] = user.username or "unknown"

        return await handler(event, data)
