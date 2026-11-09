"""Вспомогательные функции для хэндлеров."""

from __future__ import annotations

import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

logger = logging.getLogger(__name__)


async def show_in_place(
    callback: CallbackQuery, text: str, markup: InlineKeyboardMarkup | None = None
) -> None:
    """Показать текст, заменив старое сообщение (как «переход на другой экран»).

    Если отредактировать нельзя (сообщение слишком старое и т.п.) —
    просто отправляем новое сообщение. Пользователь в любом случае
    увидит нужный экран, а бот не упадёт.
    """
    message = callback.message
    if isinstance(message, Message):
        try:
            await message.edit_text(text, reply_markup=markup)
            return
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                return
            logger.info("Не удалось отредактировать сообщение: %s", e)
        await message.answer(text, reply_markup=markup)
    elif callback.from_user is not None and callback.bot is not None:
        await callback.bot.send_message(callback.from_user.id, text, reply_markup=markup)
