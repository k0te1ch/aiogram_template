def test_locales_load_and_format():
    """FTL locales parse, fall back to ru, and support {placeholder} formatting."""
    from services.context import I18nContext

    ctx = I18nContext()

    assert ctx["en"].cancel == "Cancel"
    assert ctx["ru"].cancel == "Отмена"

    # JSON list values are parsed into Python lists.
    assert ctx["en"].admin_panel_main == [["Bot", "bot"]]

    # Unknown language falls back to ru.
    assert ctx["xx"].cancel == "Отмена"


def test_locales_placeholder_formatting():
    """A localized string formats against the caller's local variables."""
    from services.context import I18nContext

    ctx = I18nContext()

    class _User:
        first_name = "Alice"

    class _Msg:
        from_user = _User()

    msg = _Msg()  # noqa: F841 — referenced via format_map on caller locals
    assert ctx["en"].already_registered == "Alice, you are already registered"
