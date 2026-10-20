"""Функции для работы с коллекцией товаров склада.

Товары хранятся в словаре products: dict[int, dict], где ключ —
идентификатор товара, а значение — словарь с его данными:
{"id", "name", "article", "category", "unit", "price", "stock"}.
"""

from typing import Dict, List, Optional, Tuple


def add_product(
    products: Dict[int, dict],
    name: str,
    article: str,
    category: str,
    unit: str,
    price: float,
    stock: int = 0,
) -> int:
    """Добавить новый товар в словарь products и вернуть его id."""
    next_id = max(products.keys(), default=0) + 1
    products[next_id] = {
        "id": next_id,
        "name": name,
        "article": article,
        "category": category,
        "unit": unit,
        "price": price,
        "stock": stock,
    }
    return next_id


def find_product(products: Dict[int, dict], query: str) -> List[dict]:
    """Найти товары, в названии или артикуле которых встречается query."""
    query_lower = query.lower()
    return [
        product
        for product in products.values()
        if query_lower in product["name"].lower()
        or query_lower in product["article"].lower()
    ]


def find_product_by_id(products: Dict[int, dict], product_id: int) -> Optional[dict]:
    """Найти товар по идентификатору."""
    return products.get(product_id)


def check_availability(
    products: Dict[int, dict], product_id: int, quantity: int = 1
) -> Tuple[bool, str]:
    """Проверить, достаточно ли товара на складе (сохранено из ПР1)."""
    product = products.get(product_id)
    if product is None:
        return False, "Товар не найден на складе"
    if product["stock"] >= quantity:
        return True, "Товар доступен"
    return False, f"Недостаточно товара. Остаток: {product['stock']} шт."


def receive_product(
    products: Dict[int, dict], product_id: int, quantity: int
) -> Tuple[bool, str]:
    """Увеличить остаток товара на складе (сохранено из ПР1)."""
    product = products.get(product_id)
    if product is None:
        return False, "Товар не найден на складе"
    if quantity <= 0:
        return False, "Количество должно быть положительным числом"
    product["stock"] += quantity
    return True, f"Принято: +{quantity} шт. Новый остаток: {product['stock']} шт."


def ship_product(
    products: Dict[int, dict], product_id: int, quantity: int
) -> Tuple[bool, str]:
    """Уменьшить остаток товара при отгрузке (сохранено из ПР1)."""
    available, message = check_availability(products, product_id, quantity)
    if not available:
        return False, message
    product = products[product_id]
    product["stock"] -= quantity
    return True, f"Отгружено: -{quantity} шт. Новый остаток: {product['stock']} шт."


def get_product_info(products: Dict[int, dict], product_id: int) -> Optional[dict]:
    """Вернуть полную информацию о товаре (сохранено из ПР1)."""
    product = products.get(product_id)
    if product is None:
        return None
    total_value = product["stock"] * product["price"]
    return {
        "id": product["id"],
        "name": product["name"],
        "article": product["article"],
        "stock": product["stock"],
        "price": product["price"],
        "total_value": total_value,
        "status": check_availability(products, product_id)[1],
    }


def filter_low_stock(products: Dict[int, dict], threshold: int = 10) -> List[dict]:
    """Отобрать товары, остаток которых ниже порогового значения."""
    return [product for product in products.values() if product["stock"] < threshold]


def sort_products_by_stock(
    products: Dict[int, dict], reverse: bool = False
) -> List[dict]:
    """Отсортировать товары по остатку на складе."""
    return sorted(products.values(), key=lambda product: product["stock"], reverse=reverse)


def show_products(products: Dict[int, dict]) -> None:
    """Вывести информацию о товарах на экран."""
    if not products:
        print("Список товаров пуст.")
        return
    for product in products.values():
        print(
            f"[{product['id']}] {product['name']} (арт. {product['article']}): "
            f"{product['stock']} {product['unit']}, категория: {product['category']}"
        )


def generate_warehouse_report(
    products: Dict[int, dict], warehouse_name: str, threshold: int = 10
) -> dict:
    """Создать отчёт по всем товарам на складе (сохранено из ПР1)."""
    total_value = 0.0
    low_stock_items = []

    for product in products.values():
        total_value += product["stock"] * product["price"]
        if product["stock"] < threshold:
            low_stock_items.append(product["name"])

    return {
        "warehouse": warehouse_name,
        "products_count": len(products),
        "total_value": total_value,
        "low_stock_items": low_stock_items,
    }
