from loguru import logger

from bot import bot
from config import API_TOKEN


async def get_my_ip():
    """
    Getting the bot's IP address
    :return: str
    """
    session = await bot.get_session()
    async with session.get("https://ipinfo.io/json") as r:
        jdata = await r.json()
        return jdata.get("ip")


async def delete_msg(chat_id, msg_id):
    """
    Deleting a message
    :param: chat_id
    :param: msg_id
    """
    session = await bot.get_session()
    async with session.get(f'https://api.telegram.org/bot{API_TOKEN}/deleteMessage?'
                           f'chat_id={chat_id}&message_id={msg_id}'):
        return


@logger.catch
async def downloadFile(url, filename, chunk_size = 65536):
    """
    Deleting a message
    :param: url
    :param: filename
    :param: chunk_size = 65536
    """
    logger.opt(colors=True).debug("The file started downloading <y>({})</y>")
    session = await bot.get_session()
    async with session.get(
        url,
        raise_for_status=True,
    ) as response:
        f = open(filename, 'wb')
        while True:
            chunk = await response.content.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            f.flush()
        f.close()
    logger.opt(colors=True).debug("<g>File downloaded <y>({})</y></g>")