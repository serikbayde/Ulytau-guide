"""Общие фикстуры для тестов.

MockedSession подменяет сетевую сессию aiogram: вместо запросов в Telegram
она запоминает, какие методы вызвал бот (sendMessage, editMessageText...).
Так мы проверяем хэндлеры целиком — через Dispatcher — без интернета.
"""

from __future__ import annotations

import sys
from datetime import datetime
from itertools import count
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from aiogram import Bot  # noqa: E402
from aiogram.client.session.base import BaseSession  # noqa: E402
from aiogram.methods import EditMessageText, GetMe, SendMessage, TelegramMethod  # noqa: E402
from aiogram.types import CallbackQuery, Chat, Message, Update, User  # noqa: E402

from bot import build_dispatcher, create_bot  # noqa: E402
from config import Settings  # noqa: E402
from services.data import GuideData  # noqa: E402
from services.i18n import I18n  # noqa: E402

USER_ID = 777
_ids = count(1)


class MockedSession(BaseSession):
    """Фейковая сессия: записывает вызовы и возвращает правдоподобные ответы."""

    def __init__(self) -> None:
        super().__init__()
        self.requests: list[TelegramMethod[Any]] = []

    async def close(self) -> None:
        pass

    async def make_request(self, bot: Bot, method: TelegramMethod[Any], timeout: int | None = None) -> Any:
        self.requests.append(method)
        if isinstance(method, (SendMessage, EditMessageText)):
            return Message(
                message_id=next(_ids),
                date=datetime.now(),
                chat=Chat(id=getattr(method, "chat_id", None) or USER_ID, type="private"),
                text=method.text,
            ).as_(bot)  # как в настоящем aiogram: объект привязан к боту
        if isinstance(method, GetMe):
            return User(id=123456, is_bot=True, first_name="Ulytau guide", username="ulytau_test_bot")
        return True

    async def stream_content(self, *args: Any, **kwargs: Any):  # pragma: no cover
        yield b""

    # --- удобные помощники для тестов ---
    def sent(self) -> list[TelegramMethod[Any]]:
        """Только сообщения (новые и отредактированные)."""
        return [r for r in self.requests if isinstance(r, (SendMessage, EditMessageText))]

    def last_text(self) -> str:
        return self.sent()[-1].text

    def clear(self) -> None:
        self.requests.clear()


class FakeGenAIClient:
    """Фейковый клиент Gemini: возвращает заданный текст или бросает ошибку."""

    def __init__(self, text: str = "Ответ гида", error: Exception | None = None) -> None:
        self.calls: list[dict] = []
        self.text = text
        self.error = error
        outer = self

        class _Models:
            async def generate_content(self, model: str, contents: str, config: Any) -> Any:
                outer.calls.append({"model": model, "contents": contents, "config": config})
                if outer.error is not None:
                    raise outer.error

                class _Resp:
                    text = outer.text

                return _Resp()

        class _Aio:
            models = _Models()

        self.aio = _Aio()


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        bot_token="123456:TEST-token-for-tests",
        gemini_api_key="",
        gemini_model="gemini-3.5-flash",
        gemini_fallback_models=("gemini-3.5-flash-lite",),
        gemini_timeout=5,
        data_dir=ROOT / "data",
        locales_dir=ROOT / "locales",
        users_file=tmp_path / "users.json",
    )


@pytest.fixture
def i18n() -> I18n:
    return I18n(ROOT / "locales")


@pytest.fixture
def guide() -> GuideData:
    return GuideData(ROOT / "data")


@pytest.fixture
def session() -> MockedSession:
    return MockedSession()


@pytest.fixture
def bot(session: MockedSession) -> Bot:
    b = create_bot("123456:TEST-token-for-tests")
    b.session = session
    return b


def make_user(lang_code: str = "ru") -> User:
    return User(id=USER_ID, is_bot=False, first_name="Тест", language_code=lang_code)


def text_update(text: str, lang_code: str = "ru") -> Update:
    """Апдейт «пользователь написал текст»."""
    msg = Message(
        message_id=next(_ids),
        date=datetime.now(),
        chat=Chat(id=USER_ID, type="private"),
        from_user=make_user(lang_code),
        text=text,
    )
    return Update(update_id=next(_ids), message=msg)


def sticker_update() -> Update:
    """Апдейт без текста (например, стикер) — упрощённо: сообщение без text."""
    msg = Message(
        message_id=next(_ids),
        date=datetime.now(),
        chat=Chat(id=USER_ID, type="private"),
        from_user=make_user(),
    )
    return Update(update_id=next(_ids), message=msg)


def callback_update(data: str, lang_code: str = "ru") -> Update:
    """Апдейт «пользователь нажал inline-кнопку»."""
    msg = Message(
        message_id=next(_ids),
        date=datetime.now(),
        chat=Chat(id=USER_ID, type="private"),
        text="previous screen",
    )
    cq = CallbackQuery(
        id=str(next(_ids)),
        from_user=make_user(lang_code),
        chat_instance="test",
        message=msg,
        data=data,
    )
    return Update(update_id=next(_ids), callback_query=cq)


@pytest.fixture
def make_dp(settings: Settings):
    """Фабрика Dispatcher: можно передать фейковый клиент Gemini."""

    def _make(ai_client: object | None = None):
        return build_dispatcher(settings, ai_client=ai_client)

    return _make
