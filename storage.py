"""Загрузка и сохранение данных приложения в формате JSON."""

import json
from typing import Dict, List


def load_products(filename: str) -> Dict[int, dict]:
    """Загрузить товары из JSON-файла в словарь products: dict[int, dict]."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка чтения файла {filename}: некорректный JSON")
        return {}

    return {item["id"]: item for item in data}


def save_products(filename: str, products: Dict[int, dict]) -> None:
    """Сохранить словарь products в JSON-файл в виде списка."""
    data = list(products.values())
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_operations(filename: str) -> List[dict]:
    """Загрузить список складских операций из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Ошибка чтения файла {filename}: некорректный JSON")
        return []


def save_operations(filename: str, operations: List[dict]) -> None:
    """Сохранить список складских операций в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(operations, file, ensure_ascii=False, indent=4)
