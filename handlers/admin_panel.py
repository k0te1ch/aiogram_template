from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from loguru import logger

from filters.dispatcher_filters import IsAdmin, IsPrivate
from keyboards import admin_main_kb, bot_commands_kb
from services import context
from utils.bot_methods import shutdown_bot

router = Router(name="admin_panel")


@router.message(Command("admin_panel"), IsPrivate, IsAdmin)
async def open_panel(msg: Message, language: str):
    logger.debug(f"[{msg.from_user.username}]: opened admin panel")
    return await msg.answer(context[language].admin_panel_open, reply_markup=admin_main_kb(language))


@router.callback_query(F.data == "bot", IsAdmin)
async def bot_menu(callback: CallbackQuery, language: str):
    logger.debug(f"[{callback.from_user.username}]: admin -> bot menu")
    await callback.answer()
    return await callback.message.edit_text(context[language].admin_panel_bot, reply_markup=bot_commands_kb(language))


@router.callback_query(F.data == "shutdown_bot", IsAdmin)
async def shutdown(callback: CallbackQuery):
    logger.debug(f"[{callback.from_user.username}]: admin -> shutdown")
    await callback.answer()
    await callback.message.answer("Bot is shutting down", reply_markup=ReplyKeyboardRemove())
    await shutdown_bot()


@router.callback_query(F.data == "back", IsAdmin)
async def back(callback: CallbackQuery, language: str):
    logger.debug(f"[{callback.from_user.username}]: admin -> back")
    await callback.answer()
    return await callback.message.edit_text(context[language].admin_panel_open, reply_markup=admin_main_kb(language))
