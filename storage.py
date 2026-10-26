"""Загрузка и сохранение данных приложения в формате JSON.

Все преобразования между JSON и объектами выполняются только в этом модуле.
"""

import json
from typing import List

from models.product import Product
from models.operation import StockOperation


def load_products(filename: str) -> list[Product]:
    """Загрузить товары из JSON-файла в список объектов Product.

    Args:
        filename: Путь к JSON-файлу.

    Returns:
        Список объектов Product.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Ошибка чтения файла {filename}: некорректный JSON")
        return []

    return [Product.from_dict(item) for item in data]


def save_products(filename: str, products: list[Product]) -> None:
    """Сохранить список объектов Product в JSON-файл.

    Args:
        filename: Путь к JSON-файлу.
        products: Список объектов Product.
    """
    data = [product.to_dict() for product in products]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_operations(
    filename: str, products_by_id: dict[int, Product]
) -> list[StockOperation]:
    """Загрузить складские операции из JSON-файла в список объектов StockOperation.

    При загрузке операции связываются с объектами Product по product_id.

    Args:
        filename: Путь к JSON-файлу.
        products_by_id: Словарь объектов Product по их id для связывания.

    Returns:
        Список объектов StockOperation.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Ошибка чтения файла {filename}: некорректный JSON")
        return []

    operations = []
    for item in data:
        try:
            operation = StockOperation.from_dict(item, products_by_id)
            operations.append(operation)
        except ValueError as e:
            print(f"Пропуск операции: {e}")

    return operations


def save_operations(filename: str, operations: list[StockOperation]) -> None:
    """Сохранить список объектов StockOperation в JSON-файл.

    Args:
        filename: Путь к JSON-файлу.
        operations: Список объектов StockOperation.
    """
    data = [operation.to_dict() for operation in operations]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)