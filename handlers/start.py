"""/start, выбор и смена языка, /help."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from handlers.callbacks import LangCb
from handlers.filters import MenuButton
from handlers.keyboards import language_keyboard, main_menu
from services.i18n import SUPPORTED_LANGS, I18n
from services.user_settings import UserSettings


def language_prompt(i18n: I18n) -> str:
    """Приветствие на трёх языках сразу — пользователь ещё не выбрал язык."""
    lines = [i18n.t(code, "choose_language") for code in SUPPORTED_LANGS]
    return "🏔 <b>Ұлытау гид</b>\n\n" + "\n".join(lines)


async def cmd_start(message: Message, i18n: I18n) -> None:
    """/start → сначала выбор языка."""
    await message.answer(language_prompt(i18n), reply_markup=language_keyboard(i18n))


async def ask_language(message: Message, i18n: I18n) -> None:
    """Кнопка «🌐 Язык» или команда /language — снова показать выбор языка."""
    await message.answer(language_prompt(i18n), reply_markup=language_keyboard(i18n))


async def language_chosen(
    callback: CallbackQuery, callback_data: LangCb, i18n: I18n, users: UserSettings
) -> None:
    """Пользователь нажал на язык → запоминаем и показываем главное меню."""
    lang = callback_data.code
    if lang not in SUPPORTED_LANGS:
        await callback.answer()
        return
    users.set_lang(callback.from_user.id, lang)
    await callback.answer(i18n.t(lang, "language_changed"))
    if isinstance(callback.message, Message):
        # Убираем кнопки выбора языка, чтобы не нажали повторно
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:  # noqa: BLE001 — не критично, если не получилось
            pass
        await callback.message.answer(i18n.t(lang, "welcome"), reply_markup=main_menu(i18n, lang))


async def cmd_help(message: Message, i18n: I18n, lang: str) -> None:
    await message.answer(i18n.t(lang, "help"), reply_markup=main_menu(i18n, lang))


def get_router() -> Router:
    router = Router(name="start")
    router.message.register(cmd_start, CommandStart())
    router.message.register(ask_language, Command("language"))
    router.message.register(ask_language, MenuButton("menu_language"))
    router.message.register(cmd_help, Command("help"))
    router.callback_query.register(language_chosen, LangCb.filter(F.code.in_(SUPPORTED_LANGS)))
    return router
