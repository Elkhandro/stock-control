"""Функции для работы со складскими операциями (приход/расход товара).

Операции хранятся в списке operations: list[dict], каждая операция —
словарь с полями: id, product_id, operation_type, quantity,
operation_date, comment, is_cancelled.
"""

from datetime import date
from typing import Dict, List, Optional

from products import receive_product, ship_product

RECEIPT = "приход"
ISSUE = "расход"
OPERATION_TYPES = (RECEIPT, ISSUE)


def create_operation(
    operations: List[dict],
    products: Dict[int, dict],
    product_id: int,
    operation_type: str,
    quantity: int,
    operation_date: date,
    comment: str = "",
) -> Optional[dict]:
    """Создать складскую операцию и изменить остаток товара.

    Возвращает None, если операция не может быть выполнена: товар не
    найден, тип операции некорректен или для расхода недостаточно
    остатка.
    """
    if operation_type not in OPERATION_TYPES:
        return None
    if product_id not in products:
        return None
    if quantity <= 0:
        return None

    if operation_type == RECEIPT:
        success, _ = receive_product(products, product_id, quantity)
    else:
        success, _ = ship_product(products, product_id, quantity)

    if not success:
        return None

    next_id = max((operation["id"] for operation in operations), default=0) + 1
    operation = {
        "id": next_id,
        "product_id": product_id,
        "operation_type": operation_type,
        "quantity": quantity,
        "operation_date": operation_date.strftime("%d.%m.%Y"),
        "comment": comment,
        "is_cancelled": False,
    }
    operations.append(operation)
    return operation


def cancel_operation(
    operations: List[dict], products: Dict[int, dict], operation_id: int
) -> bool:
    """Найти операцию по идентификатору, отменить её и вернуть остаток товара."""
    for operation in operations:
        if operation["id"] != operation_id:
            continue
        if operation["is_cancelled"]:
            return False

        product_id = operation["product_id"]
        if product_id not in products:
            return False

        if operation["operation_type"] == RECEIPT:
            ship_product(products, product_id, operation["quantity"])
        else:
            receive_product(products, product_id, operation["quantity"])

        operation["is_cancelled"] = True
        return True
    return False


def find_operations_by_product(operations: List[dict], product_id: int) -> List[dict]:
    """Вернуть операции, относящиеся к конкретному товару."""
    return [operation for operation in operations if operation["product_id"] == product_id]


def get_operation_status(operation: dict) -> str:
    """Вернуть текстовый статус операции с учётом её отмены."""
    action = "Приход" if operation["operation_type"] == RECEIPT else "Расход"
    state = "отменена" if operation["is_cancelled"] else "активна"
    return f"{action} {operation['quantity']} шт. от {operation['operation_date']} ({state})"


def show_operations(operations: List[dict]) -> None:
    """Вывести список операций на экран."""
    if not operations:
        print("Операций пока нет.")
        return
    for operation in operations:
        print(f"№{operation['id']} (товар {operation['product_id']}): "
              f"{get_operation_status(operation)}")
