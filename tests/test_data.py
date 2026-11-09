"""Проверки данных: places.json и routes.json загружаются и полные."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from services.data import GuideData, maps_url
from services.i18n import SUPPORTED_LANGS

ROOT = Path(__file__).resolve().parent.parent
KAZAKH_LETTERS = set("әғқңөұүһіӘҒҚҢӨҰҮҺІ")
LOCALIZED_PLACE_FIELDS = ("name", "description", "how_to_get", "tips", "distance_text")


def test_json_files_are_valid():
    for name in ("places.json", "routes.json"):
        with (ROOT / "data" / name).open(encoding="utf-8") as f:
            json.load(f)  # упадёт, если JSON сломан


def test_places_count(guide: GuideData):
    assert 12 <= len(guide.places) <= 15


def test_place_ids_unique(guide: GuideData):
    ids = [p["id"] for p in guide.places]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("field", LOCALIZED_PLACE_FIELDS)
def test_every_place_has_all_languages(guide: GuideData, field: str):
    for p in guide.places:
        for lang in SUPPORTED_LANGS:
            value = p[field].get(lang, "")
            assert value.strip(), f"{p['id']}: пустое поле {field}.{lang}"


def test_every_place_has_coordinates_in_ulytau_region(guide: GuideData):
    for p in guide.places:
        lat, lon = p["coordinates"]["lat"], p["coordinates"]["lon"]
        assert isinstance(lat, (int, float)) and isinstance(lon, (int, float)), p["id"]
        # Грубая рамка области Ұлытау и окрестностей Жезказгана
        assert 46.0 <= lat <= 50.5, f"{p['id']}: широта {lat} вне области"
        assert 64.0 <= lon <= 70.0, f"{p['id']}: долгота {lon} вне области"


def test_every_place_has_sources(guide: GuideData):
    for p in guide.places:
        assert p["sources"], f"{p['id']}: нет источников"
        for url in p["sources"]:
            assert re.match(r"^https?://[^\s]+$", url), f"{p['id']}: плохой URL {url}"


def test_verified_flag_and_note(guide: GuideData):
    for p in guide.places:
        assert isinstance(p["verified"], bool), p["id"]
        assert p["verification_note"].strip(), f"{p['id']}: нет комментария о проверке"


def test_kazakh_texts_use_kazakh_letters(guide: GuideData):
    """Казахский текст должен содержать специфические буквы (ә, ғ, қ, ң, ө, ұ, ү, һ, і)."""
    for p in guide.places:
        text = p["description"]["kk"] + p["how_to_get"]["kk"]
        assert set(text) & KAZAKH_LETTERS, f"{p['id']}: в казахском тексте нет казахских букв"


def test_english_descriptions_have_3_to_5_sentences(guide: GuideData):
    for p in guide.places:
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\"])", p["description"]["en"].strip())
        assert 3 <= len(sentences) <= 5, f"{p['id']}: {len(sentences)} предложений"


def test_distance_is_number(guide: GuideData):
    for p in guide.places:
        assert isinstance(p["distance_from_zhezkazgan_km"], (int, float)), p["id"]
        assert 0 <= p["distance_from_zhezkazgan_km"] <= 300, p["id"]


def test_maps_url(guide: GuideData):
    p = guide.place("alasha_khan")
    url = maps_url(p)
    assert url.startswith("https://www.google.com/maps/search/?api=1&query=")
    assert "48.3675" in url and "67.8431" in url


# --- маршруты ---


def test_three_routes(guide: GuideData):
    assert len(guide.routes) == 3
    days = sorted(r["duration_days"] for r in guide.routes)
    assert days[0] == 1  # есть однодневный маршрут


def test_routes_reference_existing_places(guide: GuideData):
    for r in guide.routes:
        assert r["stops"], r["id"]
        for stop in r["stops"]:
            assert guide.place(stop["place_id"]) is not None, f"{r['id']}: нет места {stop['place_id']}"
            assert stop["travel_min"] >= 0 and stop["travel_km"] >= 0


def test_routes_have_all_languages(guide: GuideData):
    for r in guide.routes:
        for field in ("title", "duration", "summary", "notes"):
            for lang in SUPPORTED_LANGS:
                assert r[field][lang].strip(), f"{r['id']}: пусто {field}.{lang}"
        # План маршрута одинаковой длины на всех языках
        lengths = {len(r["plan"][lang]) for lang in SUPPORTED_LANGS}
        assert len(lengths) == 1, f"{r['id']}: разное число шагов плана на разных языках"


def test_route_ids_fit_callback_limit(guide: GuideData):
    """Telegram ограничивает callback_data 64 байтами: pl:<place>:<route>."""
    for r in guide.routes:
        for stop in r["stops"]:
            data = f"pl:{stop['place_id']}:{r['id']}"
            assert len(data.encode()) <= 64, data
