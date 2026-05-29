from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from loguru import logger

from filters.dispatcher_filters import ContextButton, IsPrivate
from forms.register import Register
from keyboards import cancel_kb
from models import User, db
from services import context

router = Router(name="start")


@router.message(CommandStart(), IsPrivate)
async def start(msg: Message, state: FSMContext, language: str):
    user = db.session.get(User, msg.from_user.id) if db.enabled else None
    if user is not None:
        logger.debug(f"[{msg.from_user.username}]: already registered")
        return await msg.reply(context[language].already_registered)

    logger.debug(f"[{msg.from_user.username}]: registration started")
    await msg.reply(context[language].welcome)
    await state.set_state(Register.name)
    return await msg.answer(context[language].ask_name, reply_markup=cancel_kb(language))


@router.message(IsPrivate, ContextButton("cancel"), StateFilter(Register))
async def cancel(msg: Message, state: FSMContext, language: str):
    await state.clear()
    logger.debug(f"[{msg.from_user.username}]: registration cancelled")
    return await msg.reply(context[language].register_canceled, reply_markup=ReplyKeyboardRemove())


@router.message(IsPrivate, Register.name)
async def enter_name(msg: Message, state: FSMContext, language: str):
    await state.update_data(name=msg.text)
    await state.set_state(Register.age)
    return await msg.reply(context[language].ask_age, reply_markup=cancel_kb(language))


@router.message(IsPrivate, Register.age)
async def enter_age(msg: Message, state: FSMContext, language: str):
    if not msg.text.isnumeric() or not (8 < int(msg.text) < 100):
        logger.debug(f"[{msg.from_user.username}]: invalid age '{msg.text}'")
        return await msg.reply(context[language].invalid_input)

    await state.update_data(age=int(msg.text))
    await state.set_state(Register.phone_number)
    return await msg.reply(context[language].ask_phone_number, reply_markup=cancel_kb(language))


@router.message(IsPrivate, Register.phone_number)
async def enter_phone_number(msg: Message, state: FSMContext, language: str):
    if not msg.text.startswith("+") or not msg.text.strip("+").isnumeric():
        logger.debug(f"[{msg.from_user.username}]: invalid phone '{msg.text}'")
        return await msg.reply(context[language].invalid_input)

    data = await state.update_data(phone_number=int(msg.text.strip("+")))
    await state.clear()

    if db.enabled:
        user = User(
            id=msg.from_user.id,
            name=data["name"],
            age=data["age"],
            phone_number=data["phone_number"],
            username=msg.from_user.username,
        )
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            db.session.remove()
            logger.exception(f"[{msg.from_user.username}]: registration failed")
            return await msg.reply(context[language].error_occurred, reply_markup=ReplyKeyboardRemove())

    logger.debug(f"[{msg.from_user.username}]: registered")
    return await msg.reply(context[language].user_registered, reply_markup=ReplyKeyboardRemove())
