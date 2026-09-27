from aiogram import Bot
from loguru import logger

from .context import context
from .db import db
from .redis import redis

_bot: Bot | None = None


def init_services(bot: Bot) -> None:
    """Centralized initialization for services that need the Bot instance."""
    global _bot
    _bot = bot
    logger.debug("Services initialized")


def get_bot() -> Bot | None:
    return _bot
