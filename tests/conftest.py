import os

# Provide the minimum env so `config.Settings()` can be instantiated on import.
os.environ.setdefault("TELEGRAM_API_TOKEN", "123456:TEST")
os.environ.setdefault("LANGUAGES", '["ru", "en"]')
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("ADMINS", '["admin"]')
