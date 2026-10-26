"""Вспомогательные функции для безопасного ввода данных пользователем."""

from datetime import date, datetime


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число, повторяя запрос при ошибке."""
    while True:
        raw_value = input(prompt)
        try:
            return int(raw_value)
        except ValueError:
            print("Ошибка: введите целое число.")


def input_float(prompt: str) -> float:
    """Запросить у пользователя вещественное число, повторяя запрос при ошибке."""
    while True:
        raw_value = input(prompt)
        try:
            return float(raw_value)
        except ValueError:
            print("Ошибка: введите число (например, 1500.50).")


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ДД.ММ.ГГГГ."""
    while True:
        raw_value = input(prompt)
        try:
            return datetime.strptime(raw_value, "%d.%m.%Y").date()
        except ValueError:
            print("Ошибка: введите дату в формате ДД.ММ.ГГГГ, например 15.09.2026.")


def input_nonempty_str(prompt: str) -> str:
    """Запросить у пользователя непустую строку."""
    while True:
        raw_value = input(prompt).strip()
        if raw_value:
            return raw_value
        print("Ошибка: значение не должно быть пустым.")