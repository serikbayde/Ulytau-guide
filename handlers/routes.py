"""Раздел «🗺 Маршруты»: список маршрутов → план маршрута → места маршрута."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from handlers.callbacks import NavCb, RouteCb
from handlers.filters import MenuButton
from handlers.formatting import route_card
from handlers.keyboards import route_keyboard, routes_keyboard
from handlers.utils import show_in_place
from services.data import GuideData
from services.i18n import I18n


async def show_routes(message: Message, i18n: I18n, guide: GuideData, lang: str) -> None:
    """Кнопка «🗺 Маршруты» — список готовых маршрутов."""
    await message.answer(i18n.t(lang, "routes_title"), reply_markup=routes_keyboard(guide, lang))


async def back_to_routes(callback: CallbackQuery, i18n: I18n, guide: GuideData, lang: str) -> None:
    await callback.answer()
    await show_in_place(callback, i18n.t(lang, "routes_title"), routes_keyboard(guide, lang))


async def show_route(
    callback: CallbackQuery, callback_data: RouteCb, i18n: I18n, guide: GuideData, lang: str
) -> None:
    """План маршрута по шагам + кнопки мест маршрута."""
    route = guide.route(callback_data.id)
    if route is None:
        await callback.answer(i18n.t(lang, "route_not_found"), show_alert=True)
        return
    await callback.answer()
    await show_in_place(
        callback,
        route_card(i18n, guide, route, lang),
        route_keyboard(i18n, guide, route, lang),
    )


def get_router() -> Router:
    router = Router(name="routes")
    router.message.register(show_routes, MenuButton("menu_routes"))
    router.callback_query.register(back_to_routes, NavCb.filter(F.to == "routes"))
    router.callback_query.register(show_route, RouteCb.filter())
    return router
