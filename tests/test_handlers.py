"""Проверки хэндлеров целиком: апдейт → Dispatcher → что бот отправил.

Сеть не нужна: вместо Telegram работает MockedSession (см. conftest.py).
"""

from __future__ import annotations

from aiogram.methods import AnswerCallbackQuery, EditMessageText, SendMessage

from handlers.callbacks import LangCb, NavCb, PlaceCb, RouteCb, SourcesCb
from services.data import maps_url
from tests.conftest import FakeGenAIClient, callback_update, sticker_update, text_update


def buttons(method) -> list:
    """Все inline-кнопки из сообщения."""
    markup = method.reply_markup
    return [b for row in markup.inline_keyboard for b in row]


def reply_buttons(method) -> list[str]:
    return [b.text for row in method.reply_markup.keyboard for b in row]


async def test_start_shows_language_choice(make_dp, bot, session):
    dp = make_dp()
    await dp.feed_update(bot, text_update("/start"))
    msg = session.sent()[-1]
    assert isinstance(msg, SendMessage)
    # Приветствие на трёх языках
    assert "Тілді таңдаңыз" in msg.text and "Выберите язык" in msg.text and "Choose" in msg.text
    callbacks = [b.callback_data for b in buttons(msg)]
    assert callbacks == [LangCb(code=c).pack() for c in ("kk", "ru", "en")]


async def test_choose_kazakh_shows_main_menu(make_dp, bot, session, i18n):
    dp = make_dp()
    await dp.feed_update(bot, callback_update(LangCb(code="kk").pack()))
    welcome = [r for r in session.requests if isinstance(r, SendMessage)][-1]
    assert welcome.text == i18n.t("kk", "welcome")
    assert reply_buttons(welcome) == ["📍 Орындар", "🗺 Маршруттар", "🤖 Гидтен сұрау", "🌐 Тіл"]
    # Язык запомнился: следующий экран — на казахском
    session.clear()
    await dp.feed_update(bot, text_update("📍 Орындар"))
    assert session.last_text() == i18n.t("kk", "places_title")
    assert dp["users"].get_lang(777) == "kk"


async def test_places_list_has_all_places(make_dp, bot, session, guide):
    dp = make_dp()
    await dp.feed_update(bot, text_update("📍 Места"))
    msg = session.sent()[-1]
    assert len(buttons(msg)) == len(guide.places)
    assert all(b.callback_data.startswith("pl:") for b in buttons(msg))


async def test_place_card_with_map_button(make_dp, bot, session, guide):
    dp = make_dp()
    await dp.feed_update(bot, callback_update(PlaceCb(id="zhoshy_khan").pack()))
    edit = session.sent()[-1]
    assert isinstance(edit, EditMessageText)  # карточка заменяет список
    place = guide.place("zhoshy_khan")
    assert place["name"]["ru"] in edit.text
    assert "Как добраться" in edit.text
    btns = buttons(edit)
    assert btns[0].url == maps_url(place)  # «Открыть на карте» — Google Maps по координатам
    assert btns[1].callback_data == SourcesCb(id="zhoshy_khan").pack()
    assert btns[2].callback_data == NavCb(to="places").pack()
    assert any(isinstance(r, AnswerCallbackQuery) for r in session.requests)


async def test_unverified_place_shows_warning(make_dp, bot, session, i18n):
    dp = make_dp()
    await dp.feed_update(bot, callback_update(PlaceCb(id="dombauyl").pack()))
    assert "уточняется" in session.last_text()


async def test_sources_button(make_dp, bot, session, guide):
    dp = make_dp()
    await dp.feed_update(bot, callback_update(SourcesCb(id="alasha_khan").pack()))
    text = session.last_text()
    for url in guide.place("alasha_khan")["sources"]:
        assert url in text


async def test_unknown_place_does_not_crash(make_dp, bot, session):
    dp = make_dp()
    await dp.feed_update(bot, callback_update(PlaceCb(id="no_such_place").pack()))
    answer = [r for r in session.requests if isinstance(r, AnswerCallbackQuery)][-1]
    assert answer.show_alert


async def test_routes_list_and_route_card(make_dp, bot, session, guide):
    dp = make_dp()
    await dp.feed_update(bot, text_update("🗺 Маршруты"))
    msg = session.sent()[-1]
    assert len(buttons(msg)) == 3

    route = guide.routes[0]
    await dp.feed_update(bot, callback_update(RouteCb(id=route["id"]).pack()))
    card = session.sent()[-1]
    assert route["title"]["ru"] in card.text
    assert route["plan"]["ru"][0] in card.text
    # Кнопки мест маршрута ведут в карточку с возвратом в этот маршрут
    first_place = guide.route_place_ids(route)[0]
    assert buttons(card)[0].callback_data == PlaceCb(id=first_place, back=route["id"]).pack()
    assert buttons(card)[-1].callback_data == NavCb(to="routes").pack()


async def test_place_from_route_has_back_to_route(make_dp, bot, session, guide):
    dp = make_dp()
    route_id = guide.routes[1]["id"]
    await dp.feed_update(bot, callback_update(PlaceCb(id="aulietau", back=route_id).pack()))
    assert buttons(session.sent()[-1])[-1].callback_data == RouteCb(id=route_id).pack()


async def test_back_navigation(make_dp, bot, session, i18n):
    dp = make_dp()
    await dp.feed_update(bot, callback_update(NavCb(to="places").pack()))
    assert session.last_text() == i18n.t("ru", "places_title")
    await dp.feed_update(bot, callback_update(NavCb(to="routes").pack()))
    assert session.last_text() == i18n.t("ru", "routes_title")


async def test_language_button_works_in_any_language(make_dp, bot, session):
    dp = make_dp()
    for text in ("🌐 Тіл", "🌐 Язык", "🌐 Language"):
        session.clear()
        await dp.feed_update(bot, text_update(text))
        assert len(buttons(session.sent()[-1])) == 3


async def test_ask_without_key_gives_clear_message(make_dp, bot, session, i18n):
    dp = make_dp()  # ключа нет
    await dp.feed_update(bot, text_update("🤖 Спросить гида"))
    assert session.last_text() == i18n.t("ru", "ai_no_key")
    await dp.feed_update(bot, text_update("Как доехать до Улытау?"))
    assert session.last_text() == i18n.t("ru", "ai_no_key")


async def test_ask_with_ai(make_dp, bot, session, i18n):
    client = FakeGenAIClient(text="До села Улытау ≈130 км по трассе.")
    dp = make_dp(ai_client=client)
    await dp.feed_update(bot, text_update("🤖 Спросить гида"))
    assert session.last_text() == i18n.t("ru", "ask_intro")

    await dp.feed_update(bot, text_update("Как доехать до Улытау?"))
    texts = [m.text for m in session.sent()]
    assert i18n.t("ru", "ask_thinking") in texts  # сначала «Думаю...»
    final = session.sent()[-1]
    assert isinstance(final, EditMessageText)
    assert final.text.startswith("До села Улытау ≈130 км")
    assert final.parse_mode is None  # ответ AI — простым текстом
    assert client.calls[0]["contents"] == "Как доехать до Улытау?"


async def test_ai_error_gives_clear_message(make_dp, bot, session, i18n):
    dp = make_dp(ai_client=FakeGenAIClient(error=ConnectionError("network down")))
    await dp.feed_update(bot, text_update("Вопрос про Улытау"))
    assert session.last_text() == i18n.t("ru", "ai_unavailable")


async def test_ai_answers_in_user_language(make_dp, bot, session):
    client = FakeGenAIClient(text="Жауап")
    dp = make_dp(ai_client=client)
    await dp.feed_update(bot, callback_update(LangCb(code="en").pack()))
    await dp.feed_update(bot, text_update("Where is Ulytau?"))
    prompt = client.calls[0]["config"].system_instruction
    assert "Always answer in English" in prompt


async def test_rate_limit(make_dp, bot, session, i18n):
    dp = make_dp(ai_client=FakeGenAIClient())
    await dp.feed_update(bot, text_update("Вопрос 1"))
    await dp.feed_update(bot, text_update("Вопрос 2"))
    assert session.last_text() == i18n.t("ru", "ai_too_fast")


async def test_too_long_question(make_dp, bot, session, i18n):
    dp = make_dp(ai_client=FakeGenAIClient())
    await dp.feed_update(bot, text_update("а" * 600))
    assert session.last_text() == i18n.t("ru", "ai_too_long", max=500)


async def test_unknown_command_and_non_text(make_dp, bot, session, i18n):
    dp = make_dp()
    await dp.feed_update(bot, text_update("/unknown"))
    assert session.last_text() == i18n.t("ru", "unknown_input")
    await dp.feed_update(bot, sticker_update())
    assert session.last_text() == i18n.t("ru", "ai_text_only")


async def test_telegram_language_used_before_choice(make_dp, bot, session, i18n):
    """Если язык ещё не выбран — берём язык Telegram (en)."""
    dp = make_dp()
    await dp.feed_update(bot, text_update("/help", lang_code="en"))
    assert session.last_text() == i18n.t("en", "help")


async def test_all_place_cards_fit_telegram_limit(make_dp, bot, session, guide):
    dp = make_dp()
    for lang in ("kk", "ru", "en"):
        await dp.feed_update(bot, callback_update(LangCb(code=lang).pack()))
        for p in guide.places:
            session.clear()
            await dp.feed_update(bot, callback_update(PlaceCb(id=p["id"]).pack()))
            assert len(session.last_text()) < 4096
        for r in guide.routes:
            session.clear()
            await dp.feed_update(bot, callback_update(RouteCb(id=r["id"]).pack()))
            assert len(session.last_text()) < 4096
