"""Middleware языка: перед каждым хэндлером определяем язык пользователя
и передаём его в хэндлер как параметр `lang`."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from services.i18n import normalize_lang
from services.user_settings import UserSettings


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        users: UserSettings = data["users"]
        lang = None
        if user is not None:
            # 1) язык, который пользователь выбрал в боте;
            # 2) иначе — язык его Telegram (если это kk/ru/en), иначе русский.
            lang = users.get_lang(user.id) or normalize_lang(user.language_code)
        data["lang"] = normalize_lang(lang)
        return await handler(event, data)
