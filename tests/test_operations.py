"""Тесты функций модуля operations (уровень ПР2, без классов)."""

from datetime import date

from products import add_product
from operations import (
    ISSUE,
    RECEIPT,
    cancel_operation,
    create_operation,
    find_operations_by_product,
)


def make_products() -> dict:
    products: dict = {}
    add_product(products, "Ноутбук Lenovo", "NB-001", "Электроника", "шт.", 75000.0, 10)
    return products


def test_create_operation_receipt():
    products = make_products()
    operations: list = []
    operation = create_operation(
        operations, products, 1, RECEIPT, 5, date(2026, 9, 15)
    )
    assert operation is not None
    assert products[1]["stock"] == 15
    assert len(operations) == 1


def test_create_operation_issue_updates_stock():
    products = make_products()
    operations: list = []
    operation = create_operation(operations, products, 1, ISSUE, 4, date(2026, 9, 15))
    assert operation is not None
    assert products[1]["stock"] == 6


def test_create_operation_issue_not_enough_stock():
    products = make_products()
    operations: list = []
    operation = create_operation(operations, products, 1, ISSUE, 100, date(2026, 9, 15))
    assert operation is None
    assert products[1]["stock"] == 10
    assert len(operations) == 0


def test_create_operation_unknown_product():
    products = make_products()
    operations: list = []
    operation = create_operation(operations, products, 999, RECEIPT, 5, date(2026, 9, 15))
    assert operation is None


def test_cancel_operation_restores_stock():
    products = make_products()
    operations: list = []
    create_operation(operations, products, 1, RECEIPT, 5, date(2026, 9, 15))
    assert cancel_operation(operations, products, 1) is True
    assert products[1]["stock"] == 10
    assert operations[0]["is_cancelled"] is True


def test_cancel_operation_twice_forbidden():
    products = make_products()
    operations: list = []
    create_operation(operations, products, 1, RECEIPT, 5, date(2026, 9, 15))
    cancel_operation(operations, products, 1)
    assert cancel_operation(operations, products, 1) is False


def test_find_operations_by_product():
    products = make_products()
    operations: list = []
    create_operation(operations, products, 1, RECEIPT, 5, date(2026, 9, 15))
    create_operation(operations, products, 1, ISSUE, 2, date(2026, 9, 16))
    result = find_operations_by_product(operations, 1)
    assert len(result) == 2
