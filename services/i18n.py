"""Переводы интерфейса.

Все тексты кнопок и сообщений лежат в locales/kk.json, ru.json, en.json.
В коде мы обращаемся к ним по ключу: i18n.t("ru", "menu_places").
"""

from __future__ import annotations

import json
from pathlib import Path

# Поддерживаемые языки: қазақша, русский, English
SUPPORTED_LANGS: tuple[str, ...] = ("kk", "ru", "en")
DEFAULT_LANG = "ru"


class I18n:
    """Хранит словари переводов и отдаёт текст по ключу и языку."""

    def __init__(self, locales_dir: Path) -> None:
        self.texts: dict[str, dict[str, str]] = {}
        for lang in SUPPORTED_LANGS:
            path = Path(locales_dir) / f"{lang}.json"
            with path.open(encoding="utf-8") as f:
                self.texts[lang] = json.load(f)

    def t(self, lang: str, key: str, **kwargs: object) -> str:
        """Возвращает текст на нужном языке.

        Если языка нет — берём язык по умолчанию. Если нет ключа в выбранном
        языке — берём русский вариант, чтобы бот никогда не падал из-за перевода.
        """
        lang = normalize_lang(lang)
        text = self.texts[lang].get(key) or self.texts[DEFAULT_LANG].get(key) or key
        return text.format(**kwargs) if kwargs else text

    def variants(self, key: str) -> set[str]:
        """Все переводы одного ключа — нужно, чтобы узнавать нажатие кнопки
        меню на любом языке (например, «📍 Места» / «📍 Орындар» / «📍 Places»)."""
        return {self.texts[lang][key] for lang in SUPPORTED_LANGS if key in self.texts[lang]}


def normalize_lang(lang: str | None) -> str:
    """Приводит код языка к одному из поддерживаемых (kk/ru/en)."""
    if not lang:
        return DEFAULT_LANG
    code = lang.lower().split("-")[0]
    if code == "kz":  # иногда казахский обозначают как kz
        code = "kk"
    return code if code in SUPPORTED_LANGS else DEFAULT_LANG
