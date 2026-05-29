# config.py
# pydantic-settings based configuration + loguru logger setup.

import json
import sys
from pathlib import Path
from typing import Any

import pytz
from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # TELEGRAM BOT
    TELEGRAM_API_TOKEN: str
    SKIP_UPDATES: bool = False
    PARSE_MODE: str | None = "HTML"

    # TELEGRAM BOT API SERVER (optional, for local bot-api server)
    TG_SERVER: str | None = None
    LOCAL: bool = False

    # PROXY (e.g. socks5://127.0.0.1:1080), honoured via aiohttp trust_env
    PROXY: str | None = None

    # DEBUG / LOGGER
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # TIMEZONE
    TIMEZONE: str = "UTC"

    # DATABASE
    DATABASE: bool = False
    DATABASE_URL: str | None = None

    # REDIS — explicit URL (bare-metal) or assembled from host/port/db/password.
    REDIS_URL: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # SCHEDULER
    ENABLE_APSCHEDULER: bool = False

    # ACCESS CONTROL — JSON-encoded lists in .env, e.g. ADMINS=["k0te1ch"]
    ADMINS: list[str] = Field(default_factory=list)
    ADMINS_ID: list[int] = Field(default_factory=list)
    LANGUAGES: list[str] = Field(default_factory=lambda: ["ru", "en"])

    # DEVELOPER chat id — error middleware sends tracebacks here
    DEVELOPER: int | None = None

    # DIRECTORIES
    FILES_PATH: str = "files"
    LOGS_PATH: str = "logs"

    @field_validator("ADMINS", "ADMINS_ID", "LANGUAGES", mode="before")
    @classmethod
    def parse_json_list(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v

    @field_validator("DEVELOPER", mode="before")
    @classmethod
    def parse_developer(cls, v: Any) -> int | None:
        if v is None or (isinstance(v, str) and v.strip().lower() in ("none", "")):
            return None
        return int(v)


# -------------------------------------------------------------------
# Singleton + module-level exports
# -------------------------------------------------------------------

settings = Settings()

PROJECT_PATH = Path.cwd()
SRC_PATH = Path(__file__).parent

TIMEZONE = pytz.timezone(settings.TIMEZONE)

# Telegram
API_TOKEN = settings.TELEGRAM_API_TOKEN
SKIP_UPDATES = settings.SKIP_UPDATES
PARSE_MODE = settings.PARSE_MODE
TG_SERVER = settings.TG_SERVER
LOCAL = settings.LOCAL
PROXY = settings.PROXY

# Debug / Logger
DEBUG = settings.DEBUG
LOG_LEVEL = settings.LOG_LEVEL

# Access control
ADMINS = settings.ADMINS
ADMINS_ID = settings.ADMINS_ID
LANGUAGES = settings.LANGUAGES
DEVELOPER = settings.DEVELOPER

# Database
DATABASE = settings.DATABASE
DATABASE_URL = settings.DATABASE_URL

# Redis — explicit URL or assembled from password + host/port/db with the
# password URL-encoded (guards against @, :, /, #, ?, &, % in the secret).
_REDIS_URL = settings.REDIS_URL
if _REDIS_URL is None and settings.REDIS_PASSWORD:
    from urllib.parse import quote

    _REDIS_URL = (
        f"redis://:{quote(settings.REDIS_PASSWORD, safe='')}"
        f"@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    )
REDIS_URL = _REDIS_URL

# Scheduler
ENABLE_APSCHEDULER = settings.ENABLE_APSCHEDULER

# Paths
FILES_PATH: Path = PROJECT_PATH / settings.FILES_PATH
LOGS_PATH: Path = PROJECT_PATH / settings.LOGS_PATH


# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------


def set_up_logger(log_level: str, logs_path: Path) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level}</level>::<blue>{module}</blue>::"
            "<cyan>{function}</cyan>::<cyan>{line}</cyan> | <level>{message}</level>"
        ),
        level=log_level,
        backtrace=True,
        diagnose=True,
    )
    logger.add(
        logs_path / "file_{time:YYYY-MM-DD_HH-mm-ss}.log",
        rotation="5 MB",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level}::{module}::{function}::{line} | {message}",
        level="TRACE",
        backtrace=True,
        diagnose=True,
    )


# Create directories before configuring the file sink
for path in (FILES_PATH, LOGS_PATH):
    if not path.exists():
        try:
            path.mkdir(parents=True)
        except OSError as e:
            print(f"Error creating directory {path}: {e}", file=sys.stderr)

set_up_logger(LOG_LEVEL, LOGS_PATH)
