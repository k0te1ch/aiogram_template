from aiogram.types import BotCommand

from .admin_panel import router as admin_panel_router
from .scheduler_example import router as scheduler_example_router
from .start import router as start_router

# Order matters: more specific routers first, catch-all/start last.
ROUTERS = [
    admin_panel_router,
    scheduler_example_router,
    start_router,
]

# Commands registered via bot.set_my_commands on startup (see cli.py).
COMMANDS = [
    # BotCommand(command="start", description="Start the bot"),
    # BotCommand(command="admin_panel", description="Open the admin panel"),
]
