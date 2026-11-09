"""Раздел «🤖 Спросить гида» и обработка свободного текста.

Любой текст, который не является командой или кнопкой меню, считается
вопросом к AI-гиду. Так на сцене можно сразу писать вопрос — без лишних нажатий.
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from handlers.filters import MenuButton
from handlers.keyboards import main_menu
from services.ai_guide import STATUS_NO_KEY, STATUS_OK, AIGuide
from services.i18n import I18n
from services.rate_limit import RateLimiter

logger = logging.getLogger(__name__)

MAX_QUESTION_LEN = 500  # длинные вопросы режем — экономим квоту бесплатного тарифа
TELEGRAM_LIMIT = 4096


async def ask_intro(message: Message, i18n: I18n, lang: str, ai: AIGuide) -> None:
    """Кнопка «🤖 Спросить гида» — подсказка с примерами вопросов."""
    if not ai.available:
        await message.answer(i18n.t(lang, "ai_no_key"), reply_markup=main_menu(i18n, lang))
        return
    await message.answer(i18n.t(lang, "ask_intro"))


async def answer_question(
    message: Message, i18n: I18n, lang: str, ai: AIGuide, limiter: RateLimiter
) -> None:
    """Вопрос к AI-гиду: проверки → «Думаю...» → ответ Gemini."""
    question = (message.text or "").strip()
    if not question:
        return
    if not ai.available:
        await message.answer(i18n.t(lang, "ai_no_key"), reply_markup=main_menu(i18n, lang))
        return
    if len(question) > MAX_QUESTION_LEN:
        await message.answer(i18n.t(lang, "ai_too_long", max=MAX_QUESTION_LEN))
        return
    if message.from_user and not limiter.allow(message.from_user.id):
        await message.answer(i18n.t(lang, "ai_too_fast"))
        return

    # Показываем, что бот «печатает», и временное сообщение «Думаю...»
    try:
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:  # noqa: BLE001 — индикатор не обязателен
        pass
    thinking = await message.answer(i18n.t(lang, "ask_thinking"))

    result = await ai.ask(question, lang)
    if result.status == STATUS_OK:
        reply = f"{result.text}\n\n{i18n.t(lang, 'ai_footer')}"
    elif result.status == STATUS_NO_KEY:
        reply = i18n.t(lang, "ai_no_key")
    else:
        reply = i18n.t(lang, "ai_unavailable")
    reply = reply[:TELEGRAM_LIMIT]

    # Ответ AI отправляем простым текстом (parse_mode=None), чтобы случайные
    # символы < > & в ответе модели не сломали HTML-разметку.
    try:
        await thinking.edit_text(reply, parse_mode=None)
    except TelegramBadRequest as e:
        logger.info("Не удалось отредактировать «Думаю...»: %s", e)
        await message.answer(reply, parse_mode=None)


async def unknown_command(message: Message, i18n: I18n, lang: str) -> None:
    await message.answer(i18n.t(lang, "unknown_input"), reply_markup=main_menu(i18n, lang))


async def not_text(message: Message, i18n: I18n, lang: str) -> None:
    """Стикеры, фото, голосовые — просим написать текстом."""
    await message.answer(i18n.t(lang, "ai_text_only"), reply_markup=main_menu(i18n, lang))


def get_router() -> Router:
    router = Router(name="ask")
    router.message.register(ask_intro, MenuButton("menu_ask"))
    router.message.register(unknown_command, F.text.startswith("/"))
    router.message.register(answer_question, F.text)
    router.message.register(not_text)  # всё остальное (не текст)
    return router
