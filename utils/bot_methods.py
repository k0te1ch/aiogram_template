import sys

from loguru import logger

from services import get_bot


async def shutdown_bot() -> None:
    """Stop the bot process. Replace with graceful shutdown as needed."""
    logger.warning("Shutting down the bot by admin request")
    sys.exit(0)


async def delete_msg(chat_id: int, message_id: int) -> None:
    """Delete a message; intended for use as an APScheduler job."""
    bot = get_bot()
    if bot is None:
        logger.warning("delete_msg called before services were initialized")
        return
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        logger.warning(f"Failed to delete message {chat_id}:{message_id}: {e}")
