"""Тексты карточек мест и маршрутов (HTML-разметка Telegram).

Все данные из JSON экранируем через html.escape, чтобы символы вроде < или &
не ломали разметку сообщения.
"""

from __future__ import annotations

from html import escape

from services.data import GuideData, tr
from services.i18n import I18n

TELEGRAM_LIMIT = 4096  # максимальная длина сообщения в Telegram


def place_card(i18n: I18n, place: dict, lang: str) -> str:
    parts = [
        f"<b>{escape(tr(place['name'], lang))}</b>",
        i18n.t(lang, f"cat_{place['category']}"),
        "",
        escape(tr(place["description"], lang)),
        "",
        i18n.t(lang, "place_how_to_get"),
        escape(tr(place["how_to_get"], lang)),
        "",
        i18n.t(lang, "place_distance", distance=escape(tr(place["distance_text"], lang))),
        "",
        i18n.t(lang, "place_tips"),
        escape(tr(place["tips"], lang)),
    ]
    if not place.get("verified", False):
        parts += ["", i18n.t(lang, "place_unverified")]
    return "\n".join(parts)[:TELEGRAM_LIMIT]


def sources_text(i18n: I18n, place: dict, lang: str) -> str:
    lines = [i18n.t(lang, "sources_title", name=escape(tr(place["name"], lang)))]
    for n, url in enumerate(place.get("sources", []), start=1):
        lines.append(f"{n}. {escape(url)}")
    return "\n".join(lines)[:TELEGRAM_LIMIT]


def route_card(i18n: I18n, guide: GuideData, route: dict, lang: str) -> str:
    plan_lines = route["plan"].get(lang) or route["plan"]["ru"]
    formatted_plan = []
    for line in plan_lines:
        # Заголовки дней («ДЕНЬ 1», «СУББОТА»...) выделяем жирным
        if "—" not in line and line.isupper():
            formatted_plan.append(f"\n<b>{escape(line)}</b>")
        else:
            formatted_plan.append(f"• {escape(line)}")

    parts = [
        f"<b>{escape(tr(route['title'], lang))}</b>",
        i18n.t(lang, "route_duration", duration=escape(tr(route["duration"], lang))),
        i18n.t(lang, "route_distance", km=route.get("total_distance_km", "?")),
        "",
        escape(tr(route["summary"], lang)),
        "",
        i18n.t(lang, "route_plan"),
        *formatted_plan,
        "",
        f"ℹ️ <i>{escape(tr(route.get('notes'), lang))}</i>",
        i18n.t(lang, "route_time_note"),
        "",
        i18n.t(lang, "route_places_hint"),
    ]
    return "\n".join(parts)[:TELEGRAM_LIMIT]
