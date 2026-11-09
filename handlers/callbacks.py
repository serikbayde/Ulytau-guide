"""Данные inline-кнопок (callback_data).

aiogram сам упаковывает их в строку вида "pl:zhoshy_khan:list"
(лимит Telegram — 64 байта) и распаковывает обратно.
"""

from aiogram.filters.callback_data import CallbackData


class LangCb(CallbackData, prefix="lang"):
    """Выбор языка: kk / ru / en."""

    code: str


class PlaceCb(CallbackData, prefix="pl"):
    """Открыть карточку места. back — куда вернуться: "list" или id маршрута."""

    id: str
    back: str = "list"


class SourcesCb(CallbackData, prefix="src"):
    """Показать источники для места."""

    id: str


class RouteCb(CallbackData, prefix="rt"):
    """Открыть маршрут."""

    id: str


class NavCb(CallbackData, prefix="nav"):
    """Навигация назад: к списку мест (places) или маршрутов (routes)."""

    to: str
