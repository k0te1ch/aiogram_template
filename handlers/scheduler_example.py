# ENABLE_APSCHEDULER must be set to True in config.py file
# scheduler documentation: https://apscheduler.readthedocs.io/en/stable/
from bot import scheduler
from loguru import logger

from bot import dp
from utils.dispatcher_filters import IsPrivate
from utils.HTTP_methods import delete_msg
from datetime import datetime, timedelta


@dp.message_handler(IsPrivate, commands=['deleteit'])
async def delete_it(msg):
    m = await msg.reply("This message will be deleted in 10 seconds...")

    job_id = f'{m.chat.id}_{m.message_id}'
    delete_time = datetime.now() + timedelta(seconds=10)
    
    logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: Add job <y>(delete_it)</y> for scheduler")
    scheduler.add_job(delete_msg, 'date',
                      args=(m.chat.id, m.message_id),
                      replace_existing=True,
                      id=job_id,
                      name=job_id,
                      run_date=delete_time)
    logger.opt(colors=True).debug(f"<g>[<y>{msg.from_user.username}</y>]: Job <y>(delete_it)</y> done successful!</g>")