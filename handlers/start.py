from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.types import ReplyKeyboardRemove
from loguru import logger

from bot import context, db, dp, keyboards
from forms.register import Register
from models.user import User
from utils.dispatcher_filters import ContextButton, IsPrivate


@dp.message_handler(CommandStart(), IsPrivate)
# middleware will load and pass user to handler if it's required, check middlewares.py file
async def start(msg, user, language):
    if user is not None:
        logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: The user is already registered")
        return await msg.reply(context[language].already_registered)

    logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: User registration has started")
    await msg.reply(context.welcome)
    await Register.name.set()

    return await msg.answer(context[language].ask_name, reply_markup=keyboards["reply"][language].cancel)


@dp.message_handler(IsPrivate, ContextButton("cancel", ["ru"]), state=Register.all_states)
async def cancel(msg, state, language):
    await state.finish()

    logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: Cancellation of registration")

    return await msg.reply(context[language].register_canceled, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(IsPrivate, state=Register.name)
async def enter_name(msg, state, language):
    logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: The user entered a name \"{msg.text}\"")

    async with state.proxy() as data:
        data['name'] = msg.text

    await Register.next()

    return await msg.reply(context[language].ask_age, reply_markup=keyboards["reply"][language].cancel)


@dp.message_handler(IsPrivate, state=Register.age)
async def enter_age(msg, state, language):
    if not msg.text.isnumeric() or not (8 < int(msg.text) < 100):
        logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: The user made a mistake when entering the age \"{msg.text}\"")
        return await msg.reply(context[language].invalid_input)

    async with state.proxy() as data:
        data['age'] = int(msg.text)

    logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: The user entered the age \"{msg.text}\"")
    await Register.next()

    return await msg.reply(context[language].ask_phone_number, reply_markup=keyboards["reply"][language].cancel)


@dp.message_handler(IsPrivate, state=Register.phone_number)
async def enter_phone_number(msg, state, language):
    if not msg.text.startswith("+") or not msg.text.strip("+").isnumeric():
        logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: The user made a mistake when entering the phone number \"{msg.text}\"")
        return await msg.reply(context[language].invalid_input)

    async with state.proxy() as data:
        name = data['name']
        age = data['age']
        phone_number = int(msg.text.strip("+"))

    await state.finish()

    logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: The user entered a phone number \"{msg.text}\"")

    user = User()
    user.id = msg.from_user.id
    user.name = name
    user.age = age
    user.phone_number = phone_number
    user.username = msg.from_user.username
    db.session.add(user)

    try:
        db.session.commit()
        logger.opt(colors=True).debug(f"[<y>{msg.from_user.username}</y>]: The user has registered")
        return await msg.reply(context[language].user_registered, reply_markup=ReplyKeyboardRemove())
    except Exception:
        db.session.rollback()
        db.session.remove()
        logger.opt(colors=True).exception(f"[<y>{msg.from_user.username}</y>]: Registration failed")
        return await msg.reply(context[language].error_occurred, reply_markup=ReplyKeyboardRemove())
