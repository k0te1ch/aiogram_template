def test_settings_load_from_env():
    """Settings load the Telegram token and parse JSON list env vars."""
    from config import API_TOKEN, LANGUAGES

    assert API_TOKEN == "123456:TEST"
    assert LANGUAGES == ["ru", "en"]
