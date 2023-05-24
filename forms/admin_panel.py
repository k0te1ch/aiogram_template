from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminPanel(StatesGroup):
    main = State()
    bot = State()