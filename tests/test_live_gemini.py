"""Живая проверка с настоящим Gemini API (по умолчанию пропускается).

Запуск:  RUN_LIVE_GEMINI=1 pytest -m live -s
Нужен GEMINI_API_KEY в .env. Тратит несколько запросов бесплатной квоты.
"""

from __future__ import annotations

import os

import pytest

from config import load_settings
from services.ai_guide import STATUS_OK, AIGuide

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(os.getenv("RUN_LIVE_GEMINI") != "1", reason="RUN_LIVE_GEMINI не включён"),
]


@pytest.fixture
def live_ai(guide, i18n):
    s = load_settings()
    if not s.gemini_api_key:
        pytest.skip("GEMINI_API_KEY не задан")
    return AIGuide(s.gemini_api_key, guide, i18n, s.gemini_model, s.gemini_fallback_models, s.gemini_timeout)


async def test_answers_from_data(live_ai):
    r = await live_ai.ask("Сколько километров от Жезказгана до села Улытау?", "ru")
    print("\n[ru]", r.text)
    assert r.status == STATUS_OK
    assert "130" in r.text


async def test_says_dont_know(live_ai, i18n):
    r = await live_ai.ask("Сколько стоит билет на самолёт Астана — Жезказган?", "ru")
    print("\n[ru, нет в данных]", r.text)
    assert r.status == STATUS_OK
    assert "не знаю" in r.text.lower()


async def test_answers_in_kazakh(live_ai):
    r = await live_ai.ask("How long is the climb up Auliye-tau?", "kk")
    print("\n[kk]", r.text)
    assert r.status == STATUS_OK
    assert set(r.text) & set("әғқңөұүһі")
