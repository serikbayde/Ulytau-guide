"""Проверки AI-гида: системный промпт, отсутствие ключа, ошибки Gemini."""

from __future__ import annotations

import asyncio

from services.ai_guide import (
    STATUS_ERROR,
    STATUS_NO_KEY,
    STATUS_OK,
    AIGuide,
    build_system_prompt,
    clean_answer,
)
from services.data import GuideData
from services.i18n import SUPPORTED_LANGS, I18n
from tests.conftest import FakeGenAIClient


def make_ai(guide, i18n, client=None, timeout=5.0):
    return AIGuide(
        api_key="",
        data=guide,
        i18n=i18n,
        model="main-model",
        fallback_models=["backup-model", "main-model"],  # дубль должен игнорироваться
        timeout=timeout,
        client=client,
    )


def test_prompt_contains_all_data(guide: GuideData, i18n: I18n):
    for lang in SUPPORTED_LANGS:
        prompt = build_system_prompt(guide, i18n, lang)
        for p in guide.places:
            assert p["name"][lang] in prompt
            assert p["description"][lang] in prompt
        for r in guide.routes:
            assert r["title"][lang] in prompt
        # Фраза «не знаю» на нужном языке — в правилах
        assert i18n.t(lang, "ai_dont_know") in prompt
        assert "ONLY" in prompt


async def test_no_key_returns_status(guide, i18n):
    ai = make_ai(guide, i18n)
    assert not ai.available
    result = await ai.ask("Где мавзолей Жошы хана?", "ru")
    assert result.status == STATUS_NO_KEY


async def test_ok_answer(guide, i18n):
    client = FakeGenAIClient(text="**Мавзолей** Жошы хана в 50 км.")
    ai = make_ai(guide, i18n, client)
    result = await ai.ask("Где мавзолей?", "ru")
    assert result.status == STATUS_OK
    assert result.text == "Мавзолей Жошы хана в 50 км."  # markdown убран
    call = client.calls[0]
    assert call["model"] == "main-model"
    assert "Жошы" in call["config"].system_instruction


async def test_error_tries_fallback_then_reports(guide, i18n):
    client = FakeGenAIClient(error=RuntimeError("429 quota"))
    ai = make_ai(guide, i18n, client)
    result = await ai.ask("Вопрос", "kk")
    assert result.status == STATUS_ERROR
    assert [c["model"] for c in client.calls] == ["main-model", "backup-model"]


async def test_timeout_is_handled(guide, i18n):
    class SlowClient(FakeGenAIClient):
        def __init__(self):
            super().__init__()

            class _Models:
                async def generate_content(self, **kwargs):
                    await asyncio.sleep(10)

            class _Aio:
                models = _Models()

            self.aio = _Aio()

    ai = make_ai(guide, i18n, SlowClient(), timeout=0.05)
    result = await ai.ask("Вопрос", "en")
    assert result.status == STATUS_ERROR


async def test_empty_answer_is_error(guide, i18n):
    ai = make_ai(guide, i18n, FakeGenAIClient(text=""))
    result = await ai.ask("Вопрос", "ru")
    assert result.status == STATUS_ERROR


def test_clean_answer():
    assert clean_answer("## Заголовок\n* пункт\n**жирный**") == "Заголовок\n• пункт\nжирный"


async def test_same_question_uses_cache(guide, i18n):
    client = FakeGenAIClient(text="Ответ")
    ai = make_ai(guide, i18n, client)
    r1 = await ai.ask("Где  Улытау?", "ru")
    r2 = await ai.ask("где улытау?", "ru")  # тот же вопрос — другой регистр/пробелы
    assert r1.text == r2.text == "Ответ"
    assert len(client.calls) == 1  # второй раз Gemini не вызывался
    await ai.ask("где улытау?", "kk")  # другой язык — новый запрос
    assert len(client.calls) == 2


async def test_errors_are_not_cached(guide, i18n):
    client = FakeGenAIClient(error=RuntimeError("boom"))
    ai = make_ai(guide, i18n, client)
    await ai.ask("Вопрос", "ru")
    client.error = None
    client.text = "Теперь работает"
    assert (await ai.ask("Вопрос", "ru")).text == "Теперь работает"
