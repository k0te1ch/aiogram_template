welcome = """Привет, добро пожаловать! 👋😁

Hi, welcome! 👋😁
"""

class ru:
    cancel = "Отмена"
    back = "Назад"
    ask_name = "Ваше имя?"
    ask_age = "Сколько Вам лет?"
    ask_phone_number = "Пришлите мне Ваш номер телефона с кодом страны (например: +7xxxxxxxxxx):"
    already_registered = "Дорогой {msg.from_user.first_name}, Вы уже зарегестрированны"
    register_canceled = "Хорошо! Если Вы захотите зарегестрироваться, пришлите /start ещё раз"
    user_registered = "Вы успешно зарегестрировались"
    error_occurred = "Произошла ошибка! Пожалуйста, попробуйте снова"
    invalid_input = "Ошибка при вводе!"

    # Admin panel
    admin_panel_open = "Админ панель"
    admin_panel_close = "Админ панель закрыта"
    admin_panel_main = [("Бот", "bot")]
    bot_commands = [("Перезапустить бота", "restart_bot"), ("Выключить бота", "shutdown_bot")]


class en:
    cancel = "Cancel"
    back = "Back"
    ask_name = "Whats your name?"
    ask_age = "How old are you?"
    ask_phone_number = "Send me your phone number with code (example: +7xxxxxxxxxx):"
    already_registered = "Dear {msg.from_user.first_name}, you are already registered"
    register_canceled = "OK! if you want to register, send /start again"
    user_registered = "You have registered successfully"
    error_occurred = "An error occurred! please try again"
    invalid_input = "Invalid input!"

    # Admin panel
    admin_panel_open = "Admin panel"
    admin_panel_close = "Admin panel closed"
    admin_panel_main = [("Bot", "bot")]
    bot_commands = [("Restart the bot", "restart_bot"), ("Turn off the bot", "shutdown_bot")]
