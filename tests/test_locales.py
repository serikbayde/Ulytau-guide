"""Проверки переводов: все тексты интерфейса есть на трёх языках."""

from __future__ import annotations

import string

from services.i18n import SUPPORTED_LANGS, I18n, normalize_lang


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_all_locales_have_same_keys(i18n: I18n):
    keys = {lang: set(i18n.texts[lang]) for lang in SUPPORTED_LANGS}
    base = keys["ru"]
    for lang in SUPPORTED_LANGS:
        missing = base - keys[lang]
        extra = keys[lang] - base
        assert not missing, f"{lang}: нет ключей {missing}"
        assert not extra, f"{lang}: лишние ключи {extra}"


def test_no_empty_texts(i18n: I18n):
    for lang in SUPPORTED_LANGS:
        for key, value in i18n.texts[lang].items():
            assert value.strip(), f"{lang}.{key} пустой"


def test_same_placeholders_in_all_languages(i18n: I18n):
    for key in i18n.texts["ru"]:
        expected = placeholders(i18n.texts["ru"][key])
        for lang in SUPPORTED_LANGS:
            assert placeholders(i18n.texts[lang][key]) == expected, f"{lang}.{key}"


def test_menu_buttons_are_unique(i18n: I18n):
    """Кнопки меню не должны совпадать между собой, иначе бот их перепутает."""
    menu_keys = ("menu_places", "menu_routes", "menu_ask", "menu_language")
    all_texts = [i18n.t(lang, key) for lang in SUPPORTED_LANGS for key in menu_keys]
    assert len(all_texts) == len(set(all_texts))


def test_kazakh_locale_is_really_kazakh(i18n: I18n):
    kk_letters = set("әғқңөұүһі")
    joined = " ".join(i18n.texts["kk"].values()).lower()
    assert kk_letters & set(joined)


def test_t_fallbacks(i18n: I18n):
    assert i18n.t("xx", "menu_places") == i18n.t("ru", "menu_places")  # неизвестный язык
    assert i18n.t("ru", "no_such_key") == "no_such_key"  # неизвестный ключ — не падаем
    assert "500" in i18n.t("kk", "ai_too_long", max=500)


def test_normalize_lang():
    assert normalize_lang("kk") == "kk"
    assert normalize_lang("kz") == "kk"
    assert normalize_lang("en-US") == "en"
    assert normalize_lang("de") == "ru"
    assert normalize_lang(None) == "ru"


def test_bot_description_limits(i18n: I18n):
    """Лимиты Telegram: описание ≤ 512 символов, короткое описание ≤ 120."""
    for lang in SUPPORTED_LANGS:
        assert len(i18n.t(lang, "bot_description")) <= 512
        assert len(i18n.t(lang, "bot_short_description")) <= 120
