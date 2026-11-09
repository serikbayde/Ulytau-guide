"""Раздел «📍 Места»: список мест → карточка места → карта и источники."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from handlers.callbacks import NavCb, PlaceCb, SourcesCb
from handlers.filters import MenuButton
from handlers.formatting import place_card, sources_text
from handlers.keyboards import place_keyboard, places_keyboard
from handlers.utils import show_in_place
from services.data import GuideData
from services.i18n import I18n


async def show_places(message: Message, i18n: I18n, guide: GuideData, lang: str) -> None:
    """Кнопка «📍 Места» — список мест кнопками."""
    await message.answer(i18n.t(lang, "places_title"), reply_markup=places_keyboard(guide, lang))


async def back_to_places(callback: CallbackQuery, i18n: I18n, guide: GuideData, lang: str) -> None:
    """Кнопка «⬅️ К списку мест»."""
    await callback.answer()
    await show_in_place(callback, i18n.t(lang, "places_title"), places_keyboard(guide, lang))


async def show_place(
    callback: CallbackQuery, callback_data: PlaceCb, i18n: I18n, guide: GuideData, lang: str
) -> None:
    """Карточка места: описание, как добраться, советы, кнопка карты."""
    place = guide.place(callback_data.id)
    if place is None:
        await callback.answer(i18n.t(lang, "place_not_found"), show_alert=True)
        return
    await callback.answer()
    await show_in_place(
        callback,
        place_card(i18n, place, lang),
        place_keyboard(i18n, place, lang, back=callback_data.back),
    )


async def show_sources(
    callback: CallbackQuery, callback_data: SourcesCb, i18n: I18n, guide: GuideData, lang: str
) -> None:
    """Список ссылок-источников отдельным сообщением (карточка остаётся на месте)."""
    place = guide.place(callback_data.id)
    if place is None:
        await callback.answer(i18n.t(lang, "place_not_found"), show_alert=True)
        return
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer(sources_text(i18n, place, lang))


def get_router() -> Router:
    router = Router(name="places")
    router.message.register(show_places, MenuButton("menu_places"))
    router.callback_query.register(back_to_places, NavCb.filter(F.to == "places"))
    router.callback_query.register(show_place, PlaceCb.filter())
    router.callback_query.register(show_sources, SourcesCb.filter())
    return router
