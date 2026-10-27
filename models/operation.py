"""Модуль с классом StockOperation для представления складской операции."""

from dataclasses import dataclass
from datetime import date

from models.product import Product


RECEIPT = "приход"
ISSUE = "расход"
OPERATION_TYPES = (RECEIPT, ISSUE)


@dataclass
class StockOperation:
    """Складская операция (приход или расход товара).

    Атрибуты:
        id: Уникальный идентификатор операции.
        product: Объект Product, к которому относится операция.
        operation_type: Тип операции ("приход" или "расход").
        quantity: Количество товара в операции.
        operation_date: Дата проведения операции.
        comment: Комментарий к операции (необязательно).
        is_cancelled: Флаг отмены операции.
    """

    id: int
    product: Product
    operation_type: str
    quantity: int
    operation_date: date
    comment: str = ""
    is_cancelled: bool = False

    def __post_init__(self) -> None:
        """Проверить корректность типа операции."""
        if self.operation_type not in OPERATION_TYPES:
            raise ValueError(
                f"Некорректный тип операции: {self.operation_type}. "
                f"Допустимы: {', '.join(OPERATION_TYPES)}"
            )

    def __str__(self) -> str:
        """Строковое представление операции."""
        action = "Приход" if self.operation_type == RECEIPT else "Расход"
        state = "отменена" if self.is_cancelled else "активна"
        return (
            f"№{self.id} (товар {self.product.id}): {action} {self.quantity} "
            f"{self.product.unit} от {self.operation_date.strftime('%d.%m.%Y')} ({state})"
        )

    def cancel(self, product: Product | None = None) -> bool:
        """Отменить операцию и восстановить остаток товара.

        Args:
            product: Объект Product (если не передан, используется self.product).

        Returns:
            True, если операция успешно отменена, False — если уже отменена.
        """
        if self.is_cancelled:
            return False

        target_product = product if product is not None else self.product

        if self.operation_type == RECEIPT:
            # При отмене прихода — уменьшаем остаток (отгрузка)
            target_product.ship(self.quantity)
        else:
            # При отмене расхода — увеличиваем остаток (приём)
            target_product.receive(self.quantity)

        self.is_cancelled = True
        return True

    def get_status(self) -> str:
        """Вернуть текстовый статус операции с учётом её отмены."""
        action = "Приход" if self.operation_type == RECEIPT else "Расход"
        state = "отменена" if self.is_cancelled else "активна"
        return (
            f"{action} {self.quantity} {self.product.unit} от "
            f"{self.operation_date.strftime('%d.%m.%Y')} ({state})"
        )
    
    @property
    def display_date(self) -> str:
        """Вернуть дату в формате ДД.ММ.ГГГГ для отображения в шаблонах."""
        return self.operation_date.strftime("%d.%m.%Y")

    def to_dict(self) -> dict:
        """Преобразовать объект в словарь для сохранения в JSON.

        В JSON сохраняется product_id вместо объекта Product.
        """
        return {
            "id": self.id,
            "product_id": self.product.id,
            "operation_type": self.operation_type,
            "quantity": self.quantity,
            "operation_date": self.operation_date.strftime("%d.%m.%Y"),
            "comment": self.comment,
            "is_cancelled": self.is_cancelled,
        }

    @classmethod
    def from_dict(
        cls, data: dict, products_by_id: dict[int, Product]
    ) -> "StockOperation":
        """Создать объект StockOperation из словаря (при загрузке из JSON).

        Args:
            data: Словарь с полями операции.
            products_by_id: Словарь объектов Product по их id для связывания.

        Returns:
            Экземпляр StockOperation.
        """
        product_id = data["product_id"]
        product = products_by_id.get(product_id)
        if product is None:
            raise ValueError(
                f"Товар с id {product_id} не найден при загрузке операции"
            )

        # Парсинг даты в формате ДД.ММ.ГГГГ
        date_str = data["operation_date"]
        if isinstance(date_str, str) and "." in date_str:
            day, month, year = map(int, date_str.split("."))
            operation_date = date(year, month, day)
        else:
            operation_date = date.fromisoformat(str(date_str))

        return cls(
            id=data["id"],
            product=product,
            operation_type=data["operation_type"],
            quantity=int(data["quantity"]),
            operation_date=operation_date,
            comment=data.get("comment", ""),
            is_cancelled=bool(data.get("is_cancelled", False)),
        )