import asyncio
import os
from datetime import datetime

import click
from aiogram.types import BotCommandScopeAllPrivateChats
from alembic import command as alembic
from alembic.command import revision as alembic_revision
from alembic.config import Config
from alembic.util.exc import CommandError
from loguru import logger

import main
from config import DATABASE_URL, ENABLE_APSCHEDULER, SKIP_UPDATES
from handlers import COMMANDS
from services.scheduler import init_scheduler_jobs, scheduler


@logger.catch
def get_alembic_conf(sync: bool = True):
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL or "")
    alembic_cfg.config_file_name = os.path.join("migrations", "alembic.ini")
    if os.path.isdir("migrations") is False:
        logger.opt(colors=True).info("<light-blue>Initiating alembic...</light-blue>")
        alembic.init(alembic_cfg, "migrations", "generic" if sync else "async")
        with open("migrations/env.py", "r+") as f:
            content = f.read()
            content = content.replace(
                "target_metadata = None",
                "from models import db\ntarget_metadata = db.metadata",
            )
            f.seek(0)
            f.write(content)
            f.truncate()

    logger.debug(f"Alembic is configured ({'Sync' if sync else 'Async'})")
    return alembic_cfg


class CliGroup(click.Group):
    def list_commands(self, ctx):
        return ["showmigrations", "makemigrations", "migrate", "run"]


@click.group(cls=CliGroup)
def cli():
    pass


@logger.catch
async def _run():
    logger.info("Connecting to Telegram...")

    me = await main.bot.get_me()
    logger.opt(colors=True).info(f"Bot running as <light-blue>@{me.username}</light-blue>")

    if ENABLE_APSCHEDULER is True:
        scheduler.start()
        scheduler.remove_all_jobs()
        await init_scheduler_jobs()
        logger.success("Scheduler started and jobs initialized")

    if COMMANDS:
        await main.bot.set_my_commands(commands=COMMANDS, scope=BotCommandScopeAllPrivateChats())

    if SKIP_UPDATES:
        await main.bot.delete_webhook(drop_pending_updates=True)

    logger.success("Bot polling started!")
    await main.dp.start_polling(main.bot)


@cli.command()
@logger.catch
def run():
    asyncio.run(_run())


@logger.catch
@cli.command()
@click.option("--verbose", default=False, is_flag=True)
def showmigrations(verbose):
    cfg = get_alembic_conf()
    history = alembic.history(cfg, verbose=verbose)
    logger.info(history)


@cli.command()
@click.option("-m", "--message", default=None)
@click.option("-s", "--sync", default=True)
def makemigrations(message, sync):
    if message is None:
        message = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    try:
        cfg = get_alembic_conf(sync)
        alembic_revision(
            config=cfg,
            message=message,
            autogenerate=True,
            sql=False,
            head="head",
            splice=False,
            branch_label=None,
            version_path=None,
            rev_id=None,
        )
        logger.debug("Alembic revision created")
    except CommandError as err:
        logger.exception("Alembic command error")
        if str(err) == "Target database is not up to date.":
            logger.opt(colors=True).info('<y>Run "python cli.py migrate"</y>')


@logger.catch
@cli.command()
@click.option("-r", "--revision", default="head")
@click.option("--upgrade/--downgrade", default=True, help="Default is upgrade")
@click.option("-s", "--sync", default=True)
def migrate(revision, upgrade, sync):
    cfg = get_alembic_conf(sync)
    if upgrade is True:
        alembic.upgrade(cfg, revision)
        logger.debug("Alembic upgrade")
    else:
        alembic.downgrade(cfg, "-1" if revision == "head" else revision)
        logger.debug("Alembic downgrade")


if __name__ == "__main__":
    cli()
