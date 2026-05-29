# Demo handler for APScheduler. Requires ENABLE_APSCHEDULER=true to actually fire.
# Scheduler docs: https://apscheduler.readthedocs.io/en/stable/
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from filters.dispatcher_filters import IsPrivate
from services.scheduler import scheduler
from utils.bot_methods import delete_msg

router = Router(name="scheduler_example")


@router.message(Command("deleteit"), IsPrivate)
async def delete_it(msg: Message):
    m = await msg.reply("This message will be deleted in 10 seconds...")

    job_id = f"{m.chat.id}_{m.message_id}"
    run_date = datetime.now() + timedelta(seconds=10)

    logger.debug(f"[{msg.from_user.username}]: scheduling delete_it job")
    scheduler.add_job(
        delete_msg,
        "date",
        args=(m.chat.id, m.message_id),
        replace_existing=True,
        id=job_id,
        name=job_id,
        run_date=run_date,
    )
