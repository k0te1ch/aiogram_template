import traceback
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Update
from loguru import logger

from config import DEVELOPER


class ErrorMiddleware(BaseMiddleware):
    """Catches handler errors, logs them and notifies the developer via Telegram."""

    async def on_error(self, event, exception: Exception, data: dict[str, Any]) -> None:
        logger.error(
            f"🛑 Error while handling update:\n💥 Exception: {exception}\n🔍 Traceback:\n{traceback.format_exc()}"
        )

        if DEVELOPER is None:
            return

        user = getattr(event, "from_user", None)
        error_message = (
            f"⚠️ <b>Bot error</b>\n\n"
            f"<b>🕒 Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"<b>🆔 User:</b> {user.username if user else 'N/A'}\n"
            f"<b>💥 Error:</b>\n<pre><code>{traceback.format_exc()}</code></pre>"
        )

        try:
            await data["bot"].send_message(DEVELOPER, error_message, parse_mode="HTML")
            logger.info("📬 Error report sent to the developer.")
        except TelegramBadRequest as e:
            logger.error(f"❌ Failed to send error report to the developer: {e}")

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.warning(f"⚠️ Caught error while handling update: {e}")
            await self.on_error(event, e, data)
            raise
