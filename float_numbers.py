"""Проверка и поиск десятичных записей с точкой или экспонентой."""

import re

FLOAT_BODY = (
    r"[+-]?(?:"
    # Запись с точкой может содержать экспоненту.
    r"(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
    # Без точки наличие экспоненты обязательноa.
    r"|[0-9]+[eE][+-]?[0-9]+"
    r")"
)

FLOAT_PATTERN = re.compile(FLOAT_BODY)

# Границы нужны, чтобы обходить части слов и ошибочных числовых записей.
SEARCH_PATTERN = re.compile(
    rf"(?<![\w.+-])(?<!\d,){FLOAT_BODY}(?![\w.+-]|,\d)"
)


def is_float(value: str) -> bool:
    """Проверить формат всей строки."""
    return FLOAT_PATTERN.fullmatch(value) is not None


def find_floats(text: str) -> list[str]:
    """Вернуть найденные записи в порядке их появления в тексте."""
    return [match.group() for match in SEARCH_PATTERN.finditer(text)]
