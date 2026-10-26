"""Сервисные функции для работы со складскими операциями."""

from datetime import date

from models.operation import StockOperation, RECEIPT, ISSUE
from models.product import Product


def create_operation(
    operations: list[StockOperation],
    product: Product,
    operation_type: str,
    quantity: int,
    operation_date: date,
    comment: str = "",
) -> StockOperation | None:
    """Создать складскую операцию и изменить остаток товара.

    Args:
        operations: Список операций.
        product: Объект Product, к которому относится операция.
        operation_type: Тип операции ("приход" или "расход").
        quantity: Количество товара.
        operation_date: Дата операции.
        comment: Комментарий (необязательно).

    Returns:
        Созданный объект StockOperation или None, если операция не может быть выполнена.
    """
    if quantity <= 0:
        return None

    if operation_type == RECEIPT:
        success, _ = product.receive(quantity)
    else:
        success, _ = product.ship(quantity)

    if not success:
        return None

    next_id = max((op.id for op in operations), default=0) + 1
    operation = StockOperation(
        id=next_id,
        product=product,
        operation_type=operation_type,
        quantity=quantity,
        operation_date=operation_date,
        comment=comment,
    )
    operations.append(operation)
    return operation


def cancel_operation(
    operations: list[StockOperation], operation_id: int
) -> bool:
    """Найти операцию по идентификатору и отменить её.

    Args:
        operations: Список операций.
        operation_id: ID операции для отмены.

    Returns:
        True, если операция успешно отменена, False — если не найдена или уже отменена.
    """
    for operation in operations:
        if operation.id == operation_id:
            return operation.cancel()
    return False


def find_operations_by_product(
    operations: list[StockOperation], product_id: int
) -> list[StockOperation]:
    """Вернуть операции, относящиеся к конкретному товару.

    Args:
        operations: Список операций.
        product_id: ID товара.

    Returns:
        Список операций для указанного товара.
    """
    return [op for op in operations if op.product.id == product_id]