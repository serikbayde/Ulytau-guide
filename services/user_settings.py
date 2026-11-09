"""Запоминаем язык каждого пользователя.

Храним в простом JSON-файле (var/users.json): {"<user_id>": "kk"}.
Для конкурсного MVP этого достаточно; при росте можно заменить на SQLite/Redis.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from services.i18n import SUPPORTED_LANGS

logger = logging.getLogger(__name__)


class UserSettings:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._langs: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        try:
            with self.path.open(encoding="utf-8") as f:
                data = json.load(f)
            self._langs = {str(k): v for k, v in data.items() if v in SUPPORTED_LANGS}
        except FileNotFoundError:
            self._langs = {}
        except (OSError, ValueError) as e:
            # Повреждённый файл не должен ронять бота — начинаем с пустого
            logger.warning("Не удалось прочитать %s: %s", self.path, e)
            self._langs = {}

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            with tmp.open("w", encoding="utf-8") as f:
                json.dump(self._langs, f, ensure_ascii=False)
            os.replace(tmp, self.path)  # атомарная запись
        except OSError as e:
            logger.warning("Не удалось сохранить %s: %s", self.path, e)

    def get_lang(self, user_id: int) -> str | None:
        return self._langs.get(str(user_id))

    def set_lang(self, user_id: int, lang: str) -> None:
        if lang not in SUPPORTED_LANGS:
            raise ValueError(f"Неподдерживаемый язык: {lang}")
        self._langs[str(user_id)] = lang
        self._save()
