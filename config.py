"""Настройки бота.

Все секреты (BOT_TOKEN, GEMINI_API_KEY) читаются из файла .env или из
переменных окружения. В коде секретов нет — это важно для безопасности.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Корневая папка проекта (где лежит этот файл)
BASE_DIR = Path(__file__).resolve().parent

# Модель Gemini по умолчанию (бесплатный тариф) и запасные модели.
# На бесплатном тарифе лимит считается отдельно для каждой модели
# (≈5 запросов в минуту), поэтому при ошибке/лимите пробуем следующую.
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
DEFAULT_GEMINI_FALLBACK_MODELS = "gemini-3.5-flash-lite,gemini-3.1-flash-lite"


@dataclass(frozen=True)
class Settings:
    """Все параметры бота в одном месте."""

    bot_token: str
    gemini_api_key: str
    gemini_model: str
    gemini_fallback_models: tuple[str, ...]
    gemini_timeout: float
    data_dir: Path
    locales_dir: Path
    users_file: Path


def load_settings(env_file: Path | None = None) -> Settings:
    """Загружает настройки из .env (если он есть) и переменных окружения."""
    load_dotenv(env_file or BASE_DIR / ".env")

    return Settings(
        bot_token=os.getenv("BOT_TOKEN", "").strip(),
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip(),
        # Список через запятую, например: gemini-3.5-flash-lite,gemini-3.1-flash-lite
        gemini_fallback_models=tuple(
            m.strip()
            for m in os.getenv("GEMINI_FALLBACK_MODELS", DEFAULT_GEMINI_FALLBACK_MODELS).split(",")
            if m.strip()
        ),
        gemini_timeout=float(os.getenv("GEMINI_TIMEOUT", "40")),
        data_dir=BASE_DIR / "data",
        locales_dir=BASE_DIR / "locales",
        # Файл, где запоминаем выбранный язык каждого пользователя
        users_file=Path(os.getenv("USERS_FILE", str(BASE_DIR / "var" / "users.json"))),
    )
