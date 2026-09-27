"""Handler tests through the bot's real dispatcher: routers, filters, middlewares and FSM."""

import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import EditMessageText, SendMessage
from aiogram.types import User

from forms.register import Register

USER = User(id=100, is_bot=False, first_name="Alice", username="alice", language_code="en")
ADMIN = User(id=200, is_bot=False, first_name="Boss", username="admin", language_code="en")


@pytest.fixture
def dp() -> Dispatcher:
    """The dispatcher cli.py polls with: ``import main`` builds it once, like at startup."""
    import main

    main.dp.fsm.storage = MemoryStorage()  # a clean FSM for every test
    return main.dp


async def test_registration(dp: Dispatcher, bot_tester) -> None:
    alice = bot_tester(dp, user=USER)

    calls = await alice.send_message("/start")
    assert [call.text for call in calls.get(SendMessage)] == ["Hi, welcome! 👋😁", "What's your name?"]
    assert await alice.get_state() == Register.name

    await alice.send_message("Alice")
    (await alice.send_message("abc")).assert_called(SendMessage, text="Invalid input!")
    await alice.send_message("25")
    calls = await alice.send_message("+15550001122")

    calls.assert_called(SendMessage, text="You have registered successfully")
    assert await alice.get_state() is None


async def test_registration_can_be_cancelled(dp: Dispatcher, bot_tester) -> None:
    alice = bot_tester(dp, user=USER)
    await alice.send_message("/start")

    calls = await alice.send_message("Cancel")

    calls.assert_called(SendMessage, text="OK! If you want to register, send /start again")
    assert await alice.get_state() is None


async def test_admin_panel(dp: Dispatcher, bot_tester) -> None:
    admin = bot_tester(dp, user=ADMIN)

    (await admin.send_message("/admin_panel")).assert_called(SendMessage, text="Admin panel")
    calls = await admin.press("Bot")

    calls.assert_called(EditMessageText, text="Bot operations")


async def test_admin_panel_is_hidden_from_users(dp: Dispatcher, bot_tester) -> None:
    calls = await bot_tester(dp, user=USER).send_message("/admin_panel")

    assert len(calls) == 0
