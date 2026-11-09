"""Хэндлеры (обработчики) сообщений и нажатий кнопок.

Порядок роутеров важен: сначала команды и кнопки меню, в самом конце —
«свободный текст», который уходит AI-гиду.
"""

from aiogram import Router

from handlers import ask, errors, places, routes, start


def get_routers() -> list[Router]:
    """Создаёт новый набор роутеров (каждый вызов — новые объекты,
    поэтому приложение можно собрать несколько раз, например в тестах)."""
    return [
        start.get_router(),
        places.get_router(),
        routes.get_router(),
        ask.get_router(),  # последним: ловит любой текст
        errors.get_router(),
    ]
