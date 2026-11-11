"""Регистронезависимый LIKE для кириллицы в SQLite.

Штатный ``LIKE`` в SQLite различает регистр у не-ASCII букв, поэтому
``name__icontains="ноутбук"`` не находил «Ноутбук Lenovo». Django ORM строит
``icontains`` / ``istartswith`` / ``iexact`` именно через ``LIKE``, поэтому при
каждом подключении к SQLite подменяем функцию ``like`` версией на Python,
которая сравнивает строки без учёта регистра для любых символов Unicode.
"""

import re
from functools import lru_cache


@lru_cache(maxsize=256)
def _compile(pattern: str, escape: str | None) -> re.Pattern:
    """Преобразовать LIKE-шаблон (%, _, символ экранирования) в регулярное выражение."""
    parts = []
    chars = iter(pattern)
    for char in chars:
        if escape and char == escape:
            parts.append(re.escape(next(chars, escape)))
        elif char == "%":
            parts.append(".*")
        elif char == "_":
            parts.append(".")
        else:
            parts.append(re.escape(char))
    return re.compile("".join(parts), re.IGNORECASE | re.DOTALL)


def unicode_like(pattern, value, escape=None):
    """Аналог SQL ``value LIKE pattern [ESCAPE escape]`` без учёта регистра."""
    if pattern is None or value is None:
        return None
    return 1 if _compile(str(pattern), escape).fullmatch(str(value)) else 0


def register_unicode_like(sender, connection, **kwargs) -> None:
    """Обработчик сигнала ``connection_created``: подменить like() в SQLite."""
    if connection.vendor != "sqlite":
        return
    raw = connection.connection
    raw.create_function("like", 2, unicode_like, deterministic=True)
    raw.create_function("like", 3, unicode_like, deterministic=True)
