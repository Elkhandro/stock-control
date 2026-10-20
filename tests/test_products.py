"""Тесты функций модуля products (уровень ПР2, без классов)."""

from products import (
    add_product,
    check_availability,
    filter_low_stock,
    find_product,
    generate_warehouse_report,
    get_product_info,
    receive_product,
    ship_product,
    sort_products_by_stock,
)


def make_products() -> dict:
    products: dict = {}
    add_product(products, "Ноутбук Lenovo", "NB-001", "Электроника", "шт.", 75000.0, 15)
    add_product(products, "Монитор Samsung", "MN-002", "Электроника", "шт.", 25000.0, 8)
    return products


def test_add_product():
    products: dict = {}
    product_id = add_product(products, "Клавиатура", "KB-003", "Периферия", "шт.", 3500.0, 5)
    assert product_id == 1
    assert len(products) == 1
    assert products[1]["name"] == "Клавиатура"


def test_find_product():
    products = make_products()
    result = find_product(products, "lenovo")
    assert len(result) == 1
    assert result[0]["name"] == "Ноутбук Lenovo"


def test_check_availability():
    products = make_products()
    available, _ = check_availability(products, 1, 10)
    assert available
    available, _ = check_availability(products, 1, 100)
    assert not available


def test_receive_product():
    products = make_products()
    success, _ = receive_product(products, 1, 5)
    assert success
    assert products[1]["stock"] == 20


def test_ship_product_not_enough_stock():
    products = make_products()
    success, message = ship_product(products, 2, 50)
    assert not success
    assert "Недостаточно" in message


def test_ship_product_success():
    products = make_products()
    success, _ = ship_product(products, 1, 5)
    assert success
    assert products[1]["stock"] == 10


def test_get_product_info():
    products = make_products()
    info = get_product_info(products, 1)
    assert info is not None
    assert info["total_value"] == 15 * 75000.0


def test_filter_low_stock():
    products = make_products()
    low_stock = filter_low_stock(products, 10)
    assert len(low_stock) == 1
    assert low_stock[0]["name"] == "Монитор Samsung"


def test_sort_products_by_stock():
    products = make_products()
    sorted_products = sort_products_by_stock(products)
    assert [p["id"] for p in sorted_products] == [2, 1]


def test_generate_warehouse_report():
    products = make_products()
    report = generate_warehouse_report(products, "Тестовый склад", threshold=10)
    assert report["products_count"] == 2
    assert "Монитор Samsung" in report["low_stock_items"]
