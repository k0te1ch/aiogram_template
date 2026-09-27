import os

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.__meta__ import __version__ as aiogram_version
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp import ClientSession
from aiohttp.hdrs import USER_AGENT
from aiohttp.http import SERVER_SOFTWARE
from loguru import logger

from config import API_TOKEN, PARSE_MODE
from handlers import ROUTERS
from middlewares.base.error_middleware import ErrorMiddleware
from middlewares.base.logging_middleware import LoggingMiddleware
from middlewares.base.user_context_middleware import UserContextMiddleware
from services import init_services, redis
from services.none_module import _NoneModule

# Module name used by cli.py (`import main`) to know when to build the
# singletons below: when imported as "main" __name__ == MAIN_MODULE_NAME.
MAIN_MODULE_NAME = os.path.basename(__file__)[:-3]

logger.debug("Loading settings from config")


class TrustEnvAiohttpSession(AiohttpSession):
    """AiohttpSession that honours HTTP(S)_PROXY env vars via trust_env=True."""

    async def create_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_init),
                headers={USER_AGENT: f"{SERVER_SOFTWARE} aiogram/{aiogram_version}"},
                trust_env=True,
            )
            self._should_reset_connector = False

        return self._session


def _get_bot_obj() -> Bot:
    from config import LOCAL, TG_SERVER

    if TG_SERVER is None and LOCAL:
        from aiogram.client.telegram import TelegramAPIServer

        session = TrustEnvAiohttpSession(api=TelegramAPIServer.from_base("http://localhost:8081"))
        logger.opt(colors=True).info(
            f"Bot configured with a local server <light-blue>({session.api.base[: session.api.base.find('/bot')]})</light-blue>"
        )
    elif TG_SERVER is not None:
        from aiogram.client.telegram import TelegramAPIServer

        session = TrustEnvAiohttpSession(api=TelegramAPIServer.from_base(TG_SERVER))
        logger.opt(colors=True).info(
            f"Bot configured with a custom server <light-blue>({session.api.base[: session.api.base.find('/bot')]})</light-blue>"
        )
    else:
        session = TrustEnvAiohttpSession()
        logger.opt(colors=True).debug("The standard Telegram api server is used")

    bot = Bot(
        token=API_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=PARSE_MODE),
    )
    logger.debug("Bot is configured")
    return bot


@logger.catch
async def on_startup() -> None:
    """Run startup tasks here (set commands, warm caches, etc.)."""


@logger.catch
async def on_shutdown() -> None:
    """Run shutdown / cleanup tasks here."""


def _add_middlewares_to_observers(
    observers: list[TelegramEventObserver],
    middlewares: list[BaseMiddleware],
) -> None:
    for observer in observers:
        for middleware in middlewares:
            observer.middleware(middleware)


def _get_dp_obj(redis) -> Dispatcher:
    logger.debug("Dispatcher configuration:")
    if not isinstance(redis, _NoneModule):
        storage = RedisStorage(redis)
        logger.debug("FSM storage: Redis")
    else:
        storage = MemoryStorage()
        logger.debug("FSM storage: Memory")

    dp = Dispatcher(storage=storage)
    _add_middlewares_to_observers(
        [dp.message, dp.callback_query],
        [ErrorMiddleware(), LoggingMiddleware(), UserContextMiddleware()],
    )
    dp.include_routers(*ROUTERS)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.debug("Dispatcher is configured")
    return dp


if __name__ == MAIN_MODULE_NAME:
    bot = _get_bot_obj()
    dp = _get_dp_obj(redis)
    init_services(bot)


if __name__ == "__main__":
    from cli import cli

    logger.debug("Calling the cli module")
    cli()
