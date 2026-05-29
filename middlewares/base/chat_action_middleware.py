from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from loguru import logger


class ChatActionMiddleware(BaseMiddleware):
    """Shows a chat action (e.g. 'typing') during long operations.

    Flag a handler with ``@flags.chat_action`` or
    ``@router.message(..., flags={"long_operation": "upload_document"})``.
    """

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        action_type = get_flag(data, "long_operation")

        if not action_type:
            return await handler(event, data)

        logger.info(f"Long operation '{action_type}' started in chat {event.chat.id}")
        async with ChatActionSender(action=action_type, chat_id=event.chat.id, bot=data["bot"]):
            result = await handler(event, data)
        logger.info(f"Long operation '{action_type}' finished in chat {event.chat.id}")

        return result
