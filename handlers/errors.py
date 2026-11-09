"""Глобальный обработчик ошибок: логируем и вежливо отвечаем пользователю,
вместо того чтобы молчать. Бот при этом продолжает работать."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import ErrorEvent

from services.i18n import SUPPORTED_LANGS, I18n

logger = logging.getLogger(__name__)


async def on_error(event: ErrorEvent, i18n: I18n | None = None) -> bool:
    logger.exception("Ошибка при обработке апдейта: %s", event.exception, exc_info=event.exception)
    if i18n is None:
        return True
    # Язык здесь может быть неизвестен — отвечаем сразу на трёх языках
    text = "\n".join(i18n.t(code, "error_generic") for code in SUPPORTED_LANGS)
    update = event.update
    try:
        if update.message is not None:
            await update.message.answer(text)
        elif update.callback_query is not None:
            await update.callback_query.answer(i18n.t("ru", "error_generic"), show_alert=True)
    except Exception:  # noqa: BLE001 — если даже ответить не вышло, просто логируем
        logger.exception("Не удалось отправить сообщение об ошибке")
    return True


def get_router() -> Router:
    router = Router(name="errors")
    router.errors.register(on_error)
    return router
