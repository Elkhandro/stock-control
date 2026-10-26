"""Тесты класса Product и сервисных функций работы с товарами (уровень ПР3)."""

from models.product import Product
from services.product_service import (
    add_product,
    find_product,
    find_product_by_id,
    filter_low_stock,
    sort_products_by_stock,
    generate_warehouse_report,
)


def make_product() -> Product:
    """Создать тестовый объект Product."""
    return Product(
        id=1,
        name="Ноутбук Lenovo",
        article="NB-001",
        category="Электроника",
        unit="шт.",
        price=75000.0,
        stock=15,
    )


def make_products_list() -> list[Product]:
    """Создать список тестовых товаров."""
    return [
        Product(
            id=1,
            name="Ноутбук Lenovo",
            article="NB-001",
            category="Электроника",
            unit="шт.",
            price=75000.0,
            stock=15,
        ),
        Product(
            id=2,
            name="Монитор Samsung",
            article="MN-002",
            category="Электроника",
            unit="шт.",
            price=25000.0,
            stock=8,
        ),
    ]


def test_product_creation():
    """Тест создания объекта Product."""
    product = make_product()
    assert product.id == 1
    assert product.name == "Ноутбук Lenovo"
    assert product.stock == 15


def test_product_str():
    """Тест строкового представления Product."""
    product = make_product()
    s = str(product)
    assert "[1]" in s
    assert "Ноутбук Lenovo" in s
    assert "15" in s


def test_check_availability_sufficient():
    """Тест проверки доступности товара (достаточно)."""
    product = make_product()
    available, message = product.check_availability(10)
    assert available is True
    assert "доступен" in message.lower()


def test_check_availability_insufficient():
    """Тест проверки доступности товара (недостаточно)."""
    product = make_product()
    available, message = product.check_availability(100)
    assert available is False
    assert "недостаточно" in message.lower()


def test_receive_product():
    """Тест приёмки товара на склад."""
    product = make_product()
    success, _ = product.receive(5)
    assert success is True
    assert product.stock == 20


def test_receive_product_invalid_quantity():
    """Тест приёмки с некорректным количеством."""
    product = make_product()
    success, _ = product.receive(-5)
    assert success is False
    assert product.stock == 15


def test_ship_product_success():
    """Тест успешной отгрузки товара."""
    product = make_product()
    success, _ = product.ship(5)
    assert success is True
    assert product.stock == 10


def test_ship_product_not_enough_stock():
    """Тест отгрузки при недостаточном остатке."""
    product = make_product()
    success, message = product.ship(50)
    assert success is False
    assert "недостаточно" in message.lower()
    assert product.stock == 15


def test_get_total_value():
    """Тест расчёта общей стоимости."""
    product = make_product()
    value = product.get_total_value()
    assert value == 15 * 75000.0


def test_get_info():
    """Тест получения информации о товаре."""
    product = make_product()
    info = product.get_info()
    assert info["id"] == 1
    assert info["name"] == "Ноутбук Lenovo"
    assert info["total_value"] == 15 * 75000.0


def test_to_dict_and_from_dict():
    """Тест сериализации/десериализации Product."""
    product = make_product()
    data = product.to_dict()
    assert data["id"] == 1
    assert data["name"] == "Ноутбук Lenovo"

    restored = Product.from_dict(data)
    assert restored.id == product.id
    assert restored.name == product.name
    assert restored.stock == product.stock


def test_add_product():
    """Тест добавления товара через сервисную функцию."""
    products: list[Product] = []
    product = add_product(products, "Клавиатура", "KB-003", "Периферия", "шт.", 3500.0, 5)
    assert product.id == 1
    assert len(products) == 1
    assert product.name == "Клавиатура"


def test_find_product():
    """Тест поиска товаров."""
    products = make_products_list()
    result = find_product(products, "lenovo")
    assert len(result) == 1
    assert result[0].name == "Ноутбук Lenovo"


def test_find_product_by_id():
    """Тест поиска товара по ID."""
    products = make_products_list()
    product = find_product_by_id(products, 1)
    assert product is not None
    assert product.name == "Ноутбук Lenovo"

    missing = find_product_by_id(products, 999)
    assert missing is None


def test_filter_low_stock():
    """Тест фильтрации товаров с низким остатком."""
    products = make_products_list()
    low_stock = filter_low_stock(products, 10)
    assert len(low_stock) == 1
    assert low_stock[0].name == "Монитор Samsung"


def test_sort_products_by_stock():
    """Тест сортировки товаров по остатку."""
    products = make_products_list()
    sorted_products = sort_products_by_stock(products)
    assert [p.id for p in sorted_products] == [2, 1]


def test_generate_warehouse_report():
    """Тест генерации отчёта по складу."""
    products = make_products_list()
    report = generate_warehouse_report(products, "Тестовый склад", threshold=10)
    assert report["products_count"] == 2
    assert "Монитор Samsung" in report["low_stock_items"]