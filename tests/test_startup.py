"""Проверка запуска: импорт и инициализация без сети и без токенов."""

from __future__ import annotations

import importlib

import bot as bot_module
from config import load_settings


def test_import_all_modules():
    for name in (
        "bot",
        "config",
        "handlers",
        "handlers.start",
        "handlers.places",
        "handlers.routes",
        "handlers.ask",
        "handlers.errors",
        "services.ai_guide",
        "services.data",
        "services.i18n",
        "services.user_settings",
    ):
        importlib.import_module(name)


def test_build_dispatcher_without_keys(settings):
    dp = bot_module.build_dispatcher(settings)
    assert not dp["ai"].available  # ключа Gemini нет — но всё создаётся
    assert len(dp.sub_routers) == 5
    bot = bot_module.create_bot(settings.bot_token)
    assert bot.id == 123456


def test_dispatcher_can_be_built_twice(settings):
    bot_module.build_dispatcher(settings)
    bot_module.build_dispatcher(settings)  # роутеры создаются заново — без ошибок


async def test_main_without_token_exits_cleanly(monkeypatch, tmp_path):
    monkeypatch.setenv("BOT_TOKEN", "")
    monkeypatch.setattr(bot_module, "load_settings", lambda: load_settings(tmp_path / "none.env"))
    assert await bot_module.main() == 1


async def test_main_with_bad_token_exits_cleanly(monkeypatch, tmp_path):
    monkeypatch.setenv("BOT_TOKEN", "not-a-token")
    monkeypatch.setattr(bot_module, "load_settings", lambda: load_settings(tmp_path / "none.env"))
    assert await bot_module.main() == 1


def test_user_settings_persist(tmp_path):
    from services.user_settings import UserSettings

    path = tmp_path / "users.json"
    UserSettings(path).set_lang(1, "kk")
    assert UserSettings(path).get_lang(1) == "kk"  # язык сохранился после «перезапуска»
    path.write_text("{broken json")
    assert UserSettings(path).get_lang(1) is None  # битый файл не роняет бота


async def test_wait_for_telegram_retries_until_network_is_back(bot, session, monkeypatch):
    """Нет сети при старте → бот не падает, а повторяет попытки."""
    from aiogram.exceptions import TelegramNetworkError
    from aiogram.methods import GetMe

    attempts = {"n": 0}
    original = session.make_request

    async def flaky(bot_, method, timeout=None):
        if isinstance(method, GetMe) and attempts["n"] < 2:
            attempts["n"] += 1
            raise TelegramNetworkError(method=method, message="DNS error")
        return await original(bot_, method, timeout)

    async def no_sleep(_):
        return None

    monkeypatch.setattr(session, "make_request", flaky)
    monkeypatch.setattr(bot_module.asyncio, "sleep", no_sleep)
    me = await bot_module.wait_for_telegram(bot)
    assert me.username == "ulytau_test_bot"
    assert attempts["n"] == 2


async def test_main_with_rejected_token_exits_cleanly(monkeypatch, tmp_path, bot, session):
    """Токен правильного формата, но Telegram его отклонил → понятный выход с кодом 1."""
    from aiogram.exceptions import TelegramUnauthorizedError

    async def unauthorized(bot_, method, timeout=None):
        raise TelegramUnauthorizedError(method=method, message="Unauthorized")

    monkeypatch.setenv("BOT_TOKEN", "123456:TEST-token-for-tests")
    monkeypatch.setenv("USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr(bot_module, "load_settings", lambda: load_settings(tmp_path / "none.env"))
    monkeypatch.setattr(session, "make_request", unauthorized)
    monkeypatch.setattr(bot_module, "create_bot", lambda token: bot)
    assert await bot_module.main() == 1


async def test_setup_bot_profile_sets_commands_and_descriptions(bot, session, i18n):
    from aiogram.methods import SetMyCommands, SetMyDescription, SetMyShortDescription

    await bot_module.setup_bot_profile(bot, i18n)
    langs = [r.language_code for r in session.requests if isinstance(r, SetMyCommands)]
    assert langs == ["kk", "ru", "en", None]  # 3 языка + вариант по умолчанию
    assert sum(isinstance(r, SetMyDescription) for r in session.requests) == 4
    assert sum(isinstance(r, SetMyShortDescription) for r in session.requests) == 4
