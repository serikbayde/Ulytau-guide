"""Клавиатуры: главное меню (снизу) и inline-кнопки под сообщениями."""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from handlers.callbacks import LangCb, NavCb, PlaceCb, RouteCb, SourcesCb
from services.data import GuideData, maps_url, tr
from services.i18n import SUPPORTED_LANGS, I18n

# Иконка для каждой категории места
CATEGORY_ICONS = {"sacred": "🕌", "history": "🏛", "nature": "🏔", "city": "🏙"}


def language_keyboard(i18n: I18n) -> InlineKeyboardMarkup:
    """Три кнопки выбора языка."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t(code, "lang_name"), callback_data=LangCb(code=code).pack()
                )
            ]
            for code in SUPPORTED_LANGS
        ]
    )


def main_menu(i18n: I18n, lang: str) -> ReplyKeyboardMarkup:
    """Главное меню 2×2 внизу экрана."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=i18n.t(lang, "menu_places")),
                KeyboardButton(text=i18n.t(lang, "menu_routes")),
            ],
            [
                KeyboardButton(text=i18n.t(lang, "menu_ask")),
                KeyboardButton(text=i18n.t(lang, "menu_language")),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def places_keyboard(guide: GuideData, lang: str) -> InlineKeyboardMarkup:
    """Список мест — по одной кнопке на место."""
    rows = [
        [
            InlineKeyboardButton(
                text=f"{CATEGORY_ICONS.get(p['category'], '📍')} {tr(p['name'], lang)}",
                callback_data=PlaceCb(id=p["id"]).pack(),
            )
        ]
        for p in guide.places
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def place_keyboard(i18n: I18n, place: dict, lang: str, back: str) -> InlineKeyboardMarkup:
    """Кнопки под карточкой места: карта, источники, назад."""
    if back == "list":
        back_button = InlineKeyboardButton(
            text=i18n.t(lang, "btn_back_places"), callback_data=NavCb(to="places").pack()
        )
    else:  # пришли из маршрута — возвращаемся в него
        back_button = InlineKeyboardButton(
            text=i18n.t(lang, "btn_back_routes"), callback_data=RouteCb(id=back).pack()
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i18n.t(lang, "btn_open_map"), url=maps_url(place))],
            [
                InlineKeyboardButton(
                    text=i18n.t(lang, "btn_sources", count=len(place.get("sources", []))),
                    callback_data=SourcesCb(id=place["id"]).pack(),
                )
            ],
            [back_button],
        ]
    )


def routes_keyboard(guide: GuideData, lang: str) -> InlineKeyboardMarkup:
    """Список маршрутов."""
    rows = [
        [
            InlineKeyboardButton(
                text=f"🧭 {tr(r['title'], lang)} · {tr(r['duration'], lang)}",
                callback_data=RouteCb(id=r["id"]).pack(),
            )
        ]
        for r in guide.routes
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def route_keyboard(i18n: I18n, guide: GuideData, route: dict, lang: str) -> InlineKeyboardMarkup:
    """Кнопки мест маршрута + «назад к маршрутам»."""
    rows = []
    for pid in guide.route_place_ids(route):
        place = guide.place(pid)
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{CATEGORY_ICONS.get(place['category'], '📍')} {tr(place['name'], lang)}",
                    callback_data=PlaceCb(id=pid, back=route["id"]).pack(),
                )
            ]
        )
    rows.append(
        [InlineKeyboardButton(text=i18n.t(lang, "btn_back_routes"), callback_data=NavCb(to="routes").pack())]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
