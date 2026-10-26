"""Сервисные функции для работы с коллекцией товаров."""

from models.product import Product


def add_product(
    products: list[Product],
    name: str,
    article: str,
    category: str,
    unit: str,
    price: float,
    stock: int = 0,
) -> Product:
    """Создать новый товар и добавить его в коллекцию.

    Args:
        products: Список товаров.
        name: Наименование товара.
        article: Артикул товара.
        category: Категория товара.
        unit: Единица измерения.
        price: Цена за единицу.
        stock: Начальный остаток (по умолчанию 0).

    Returns:
        Созданный объект Product.
    """
    next_id = max((p.id for p in products), default=0) + 1
    product = Product(
        id=next_id,
        name=name,
        article=article,
        category=category,
        unit=unit,
        price=price,
        stock=stock,
    )
    products.append(product)
    return product


def find_product(products: list[Product], query: str) -> list[Product]:
    """Найти товары, в названии или артикуле которых встречается query.

    Args:
        products: Список товаров.
        query: Строка поиска.

    Returns:
        Список найденных товаров.
    """
    query_lower = query.lower()
    return [
        product
        for product in products
        if query_lower in product.name.lower()
        or query_lower in product.article.lower()
    ]


def find_product_by_id(products: list[Product], product_id: int) -> Product | None:
    """Найти товар по идентификатору.

    Args:
        products: Список товаров.
        product_id: ID искомого товара.

    Returns:
        Найденный объект Product или None.
    """
    for product in products:
        if product.id == product_id:
            return product
    return None


def filter_low_stock(products: list[Product], threshold: int = 10) -> list[Product]:
    """Отобрать товары, остаток которых ниже порогового значения.

    Args:
        products: Список товаров.
        threshold: Пороговое значение остатка.

    Returns:
        Список товаров с низким остатком.
    """
    return [product for product in products if product.stock < threshold]


def sort_products_by_stock(
    products: list[Product], reverse: bool = False
) -> list[Product]:
    """Отсортировать товары по остатку на складе.

    Args:
        products: Список товаров.
        reverse: Сортировать по убыванию, если True.

    Returns:
        Отсортированный список товаров.
    """
    return sorted(products, key=lambda p: p.stock, reverse=reverse)


def generate_warehouse_report(
    products: list[Product], warehouse_name: str, threshold: int = 10
) -> dict:
    """Создать отчёт по всем товарам на складе.

    Args:
        products: Список товаров.
        warehouse_name: Название склада.
        threshold: Пороговое значение остатка для отчёта.

    Returns:
        Словарь с данными отчёта.
    """
    total_value = 0.0
    low_stock_items = []

    for product in products:
        total_value += product.get_total_value()
        if product.stock < threshold:
            low_stock_items.append(product.name)

    return {
        "warehouse": warehouse_name,
        "products_count": len(products),
        "total_value": total_value,
        "low_stock_items": low_stock_items,
    }