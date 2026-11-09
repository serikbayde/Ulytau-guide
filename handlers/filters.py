"""Фильтр для кнопок главного меню.

Кнопки меню — это обычный текст на выбранном языке. Фильтр проверяет,
совпадает ли текст сообщения с кнопкой на ЛЮБОМ из трёх языков —
так кнопки работают даже сразу после смены языка.
"""

from aiogram.filters import Filter
from aiogram.types import Message

from services.i18n import I18n


class MenuButton(Filter):
    def __init__(self, key: str) -> None:
        self.key = key

    async def __call__(self, message: Message, i18n: I18n) -> bool:
        return message.text is not None and message.text in i18n.variants(self.key)
