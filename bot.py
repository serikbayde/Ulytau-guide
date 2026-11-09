"""Точка входа Telegram-бота «Ұлытау гид».

Запуск:  python bot.py

Что происходит при старте:
1. читаем настройки из .env (BOT_TOKEN, GEMINI_API_KEY);
2. загружаем данные (места, маршруты) и переводы интерфейса;
3. собираем Dispatcher с хэндлерами и запускаем long polling.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, User
from aiogram.utils.token import TokenValidationError

from config import Settings, load_settings
from handlers import get_routers
from handlers.middleware import LanguageMiddleware
from services.ai_guide import AIGuide
from services.data import GuideData
from services.i18n import SUPPORTED_LANGS, I18n
from services.rate_limit import RateLimiter
from services.user_settings import UserSettings

logger = logging.getLogger("ulytau_guide")


def build_dispatcher(settings: Settings, ai_client: object | None = None) -> Dispatcher:
    """Создаёт Dispatcher и передаёт в него все сервисы.

    Объекты i18n, guide, users, ai, limiter aiogram сам подставит в хэндлеры
    по имени параметра (dependency injection).
    """
    i18n = I18n(settings.locales_dir)
    guide = GuideData(settings.data_dir)
    users = UserSettings(settings.users_file)
    ai = AIGuide(
        api_key=settings.gemini_api_key,
        data=guide,
        i18n=i18n,
        model=settings.gemini_model,
        fallback_models=settings.gemini_fallback_models,
        timeout=settings.gemini_timeout,
        client=ai_client,
    )

    dp = Dispatcher(
        storage=MemoryStorage(),
        i18n=i18n,
        guide=guide,
        users=users,
        ai=ai,
        limiter=RateLimiter(interval_seconds=4),
    )
    # Middleware определяет язык пользователя перед каждым хэндлером
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.include_routers(*get_routers())
    return dp


def create_bot(token: str) -> Bot:
    """Bot с HTML-разметкой по умолчанию и без превью ссылок."""
    return Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True),
    )


def bot_commands(i18n: I18n, lang: str) -> list[BotCommand]:
    return [
        BotCommand(command="start", description=i18n.t(lang, "cmd_start")),
        BotCommand(command="language", description=i18n.t(lang, "cmd_language")),
        BotCommand(command="help", description=i18n.t(lang, "cmd_help")),
    ]


async def setup_bot_profile(bot: Bot, i18n: I18n) -> None:
    """Меню команд и описание бота на трёх языках.

    Описание пользователь видит в пустом чате до нажатия /start.
    Язык выбирается Telegram автоматически по языку приложения пользователя;
    вариант без language_code — по умолчанию (русский).
    Ошибка здесь не критична: бот всё равно работает.
    """
    try:
        for lang in (*SUPPORTED_LANGS, None):
            text_lang = lang or "ru"
            await bot.set_my_commands(bot_commands(i18n, text_lang), language_code=lang)
            await bot.set_my_description(i18n.t(text_lang, "bot_description"), language_code=lang)
            await bot.set_my_short_description(
                i18n.t(text_lang, "bot_short_description"), language_code=lang
            )
    except Exception as e:  # noqa: BLE001
        logger.warning("Не удалось настроить команды/описание бота: %s", e)


async def wait_for_telegram(bot: Bot, max_delay: float = 60.0) -> User:
    """Ждём, пока Telegram станет доступен (например, сервер только загрузился
    и сети ещё нет). Пауза между попытками растёт: 2, 4, 8 ... до 60 секунд.
    Неверный токен (TelegramUnauthorizedError) пробрасываем — ждать бессмысленно."""
    delay = 2.0
    while True:
        try:
            return await bot.get_me()
        except TelegramNetworkError as e:
            logger.warning("Нет связи с Telegram (%s). Повтор через %.0f с", e, delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay)


async def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = load_settings()

    if not settings.bot_token:
        logger.error("BOT_TOKEN не задан. Скопируйте .env.example в .env и впишите токен от @BotFather.")
        return 1
    try:
        bot = create_bot(settings.bot_token)
    except TokenValidationError:
        logger.error("BOT_TOKEN имеет неверный формат. Проверьте значение в .env.")
        return 1

    dp = build_dispatcher(settings)
    if not dp["ai"].available:
        logger.warning("GEMINI_API_KEY не задан — бот работает, AI-гид отвечает сообщением о недоступности.")
    else:
        logger.info("AI-гид: модель %s, запасные: %s", settings.gemini_model, ", ".join(settings.gemini_fallback_models))

    try:
        try:
            me = await wait_for_telegram(bot)
        except TelegramUnauthorizedError:
            logger.error("Telegram отклонил BOT_TOKEN (неверный или отозван). Проверьте токен у @BotFather.")
            return 1
        logger.info("Подключено к Telegram как @%s", me.username)

        await setup_bot_profile(bot, dp["i18n"])
        try:
            # Сбрасываем вебхук (если был) и старые апдейты, затем — long polling
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception as e:  # noqa: BLE001
            logger.warning("Не удалось сбросить вебхук: %s", e)
        logger.info("Бот запущен. Остановка: Ctrl+C")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
