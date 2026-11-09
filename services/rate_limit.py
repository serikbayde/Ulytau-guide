"""Простое ограничение частоты вопросов к AI.

Бесплатный тариф Gemini ограничен по числу запросов в минуту, поэтому
один пользователь может задавать вопрос не чаще, чем раз в N секунд.
"""

from __future__ import annotations

import time


class RateLimiter:
    def __init__(self, interval_seconds: float = 4.0) -> None:
        self.interval = interval_seconds
        self._last: dict[int, float] = {}

    def allow(self, user_id: int) -> bool:
        """True — можно отправлять запрос; False — слишком часто."""
        now = time.monotonic()
        last = self._last.get(user_id)
        if last is not None and now - last < self.interval:
            return False
        self._last[user_id] = now
        return True
