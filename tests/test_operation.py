"""Тесты класса StockOperation и сервисных функций работы с операциями (уровень ПР3)."""

from datetime import date

from models.product import Product
from models.operation import StockOperation, RECEIPT, ISSUE
from services.operation_service import (
    create_operation,
    cancel_operation,
    find_operations_by_product,
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
        stock=10,
    )


def make_products_list() -> list[Product]:
    """Создать список тестовых товаров."""
    return [make_product()]


def test_operation_creation():
    """Тест создания объекта StockOperation."""
    product = make_product()
    operation = StockOperation(
        id=1,
        product=product,
        operation_type=RECEIPT,
        quantity=5,
        operation_date=date(2026, 9, 15),
        comment="Плановая поставка",
    )
    assert operation.id == 1
    assert operation.product == product
    assert operation.is_cancelled is False


def test_operation_str():
    """Тест строкового представления StockOperation."""
    product = make_product()
    operation = StockOperation(
        id=1,
        product=product,
        operation_type=RECEIPT,
        quantity=5,
        operation_date=date(2026, 9, 15),
    )
    s = str(operation)
    assert "№1" in s
    assert "Приход" in s
    assert "5" in s


def test_operation_invalid_type():
    """Тест создания операции с некорректным типом."""
    product = make_product()
    try:
        StockOperation(
            id=1,
            product=product,
            operation_type="неизвестный",
            quantity=5,
            operation_date=date(2026, 9, 15),
        )
        assert False, "Должно было быть исключение ValueError"
    except ValueError as e:
        assert "Некорректный тип операции" in str(e)


def test_cancel_operation_receipt():
    """Тест отмены операции прихода (остаток должен уменьшиться)."""
    product = make_product()
    operation = StockOperation(
        id=1,
        product=product,
        operation_type=RECEIPT,
        quantity=5,
        operation_date=date(2026, 9, 15),
    )
    # Предварительно увеличим остаток (как если бы приход был выполнен)
    product.receive(5)
    assert product.stock == 15

    result = operation.cancel()
    assert result is True
    assert operation.is_cancelled is True
    assert product.stock == 10  # Остаток восстановлен


def test_cancel_operation_issue():
    """Тест отмены операции расхода (остаток должен увеличиться)."""
    product = make_product()
    operation = StockOperation(
        id=1,
        product=product,
        operation_type=ISSUE,
        quantity=5,
        operation_date=date(2026, 9, 15),
    )
    # Предварительно уменьшим остаток (как если бы расход был выполнен)
    product.ship(5)
    assert product.stock == 5

    result = operation.cancel()
    assert result is True
    assert operation.is_cancelled is True
    assert product.stock == 10  # Остаток восстановлен


def test_cancel_operation_twice():
    """Тест двойной отмены операции (должна вернуть False)."""
    product = make_product()
    operation = StockOperation(
        id=1,
        product=product,
        operation_type=RECEIPT,
        quantity=5,
        operation_date=date(2026, 9, 15),
    )
    product.receive(5)
    operation.cancel()
    result = operation.cancel()
    assert result is False


def test_create_operation_receipt():
    """Тест создания операции прихода через сервисную функцию."""
    products = make_products_list()
    operations: list[StockOperation] = []
    operation = create_operation(
        operations, products[0], RECEIPT, 5, date(2026, 9, 15)
    )
    assert operation is not None
    assert products[0].stock == 15
    assert len(operations) == 1


def test_create_operation_issue_updates_stock():
    """Тест создания операции расхода (остаток уменьшается)."""
    products = make_products_list()
    operations: list[StockOperation] = []
    operation = create_operation(
        operations, products[0], ISSUE, 4, date(2026, 9, 15)
    )
    assert operation is not None
    assert products[0].stock == 6


def test_create_operation_issue_not_enough_stock():
    """Тест создания операции расхода при недостаточном остатке."""
    products = make_products_list()
    operations: list[StockOperation] = []
    operation = create_operation(
        operations, products[0], ISSUE, 100, date(2026, 9, 15)
    )
    assert operation is None
    assert products[0].stock == 10
    assert len(operations) == 0


def test_cancel_operation_service():
    """Тест отмены операции через сервисную функцию."""
    products = make_products_list()
    operations: list[StockOperation] = []
    create_operation(operations, products[0], RECEIPT, 5, date(2026, 9, 15))
    assert cancel_operation(operations, 1) is True
    assert products[0].stock == 10
    assert operations[0].is_cancelled is True


def test_cancel_operation_twice_service():
    """Тест двойной отмены через сервисную функцию."""
    products = make_products_list()
    operations: list[StockOperation] = []
    create_operation(operations, products[0], RECEIPT, 5, date(2026, 9, 15))
    cancel_operation(operations, 1)
    assert cancel_operation(operations, 1) is False


def test_find_operations_by_product():
    """Тест поиска операций по товару."""
    products = make_products_list()
    operations: list[StockOperation] = []
    create_operation(operations, products[0], RECEIPT, 5, date(2026, 9, 15))
    create_operation(operations, products[0], ISSUE, 2, date(2026, 9, 16))
    result = find_operations_by_product(operations, 1)
    assert len(result) == 2


def test_operation_to_dict_and_from_dict():
    """Тест сериализации/десериализации StockOperation."""
    product = make_product()
    operation = StockOperation(
        id=1,
        product=product,
        operation_type=RECEIPT,
        quantity=5,
        operation_date=date(2026, 9, 15),
        comment="Тест",
    )
    data = operation.to_dict()
    assert data["id"] == 1
    assert data["product_id"] == 1
    assert data["operation_type"] == "приход"

    products_by_id = {product.id: product}
    restored = StockOperation.from_dict(data, products_by_id)
    assert restored.id == operation.id
    assert restored.product.id == product.id
    assert restored.operation_type == operation.operation_type