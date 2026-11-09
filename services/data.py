"""Загрузка данных о местах и маршрутах из data/places.json и data/routes.json."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

from services.i18n import DEFAULT_LANG, normalize_lang


class GuideData:
    """Достопримечательности и маршруты, загруженные из JSON-файлов."""

    def __init__(self, data_dir: Path) -> None:
        data_dir = Path(data_dir)
        with (data_dir / "places.json").open(encoding="utf-8") as f:
            places_json = json.load(f)
        with (data_dir / "routes.json").open(encoding="utf-8") as f:
            routes_json = json.load(f)

        self.places_meta: dict = places_json.get("meta", {})
        self.routes_meta: dict = routes_json.get("meta", {})
        self.places: list[dict] = places_json["places"]
        self.routes: list[dict] = routes_json["routes"]

        # Словари для быстрого поиска по id
        self._places_by_id = {p["id"]: p for p in self.places}
        self._routes_by_id = {r["id"]: r for r in self.routes}

    def place(self, place_id: str) -> dict | None:
        return self._places_by_id.get(place_id)

    def route(self, route_id: str) -> dict | None:
        return self._routes_by_id.get(route_id)

    def route_place_ids(self, route: dict) -> list[str]:
        """Уникальные id мест маршрута в порядке посещения."""
        result: list[str] = []
        for stop in route.get("stops", []):
            pid = stop["place_id"]
            if pid not in result and pid in self._places_by_id:
                result.append(pid)
        return result


def tr(field: dict | str | None, lang: str) -> str:
    """Берёт из поля {"kk": ..., "ru": ..., "en": ...} текст на нужном языке."""
    if field is None:
        return ""
    if isinstance(field, str):
        return field
    lang = normalize_lang(lang)
    return field.get(lang) or field.get(DEFAULT_LANG) or next(iter(field.values()), "")


def maps_url(place: dict) -> str:
    """Ссылка «Открыть на карте» — Google Maps по координатам места."""
    lat = place["coordinates"]["lat"]
    lon = place["coordinates"]["lon"]
    return f"https://www.google.com/maps/search/?api=1&query={quote(f'{lat},{lon}')}"
