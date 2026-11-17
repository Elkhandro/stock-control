"""Django ORM-модель складской операции (ПР9).

Не путать с классом ``StockOperation`` из пакета ``models/`` (ПР3).
"""

from django.db import models

from products.models import Product

class OperationType(models.TextChoices):
    """Допустимые направления движения товара."""

    RECEIPT = "приход", "Приход"
    ISSUE = "расход", "Расход"


class OperationStatus(models.TextChoices):
    """Состояние записи складской операции."""

    ACTIVE = "active", "Активна"
    CANCELLED = "cancelled", "Отменена"


RECEIPT = OperationType.RECEIPT
ISSUE = OperationType.ISSUE
OPERATION_TYPE_CHOICES = OperationType.choices


class Operation(models.Model):
    """Складская операция (приход или расход товара).

    ``on_delete=PROTECT`` — товар, по которому есть история операций,
    нельзя удалить случайно: история движения товара сохраняется.
    ``related_name="operations"`` — обратный доступ ``product.operations.all()``.
    """

    Status = OperationStatus

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="operations",
        verbose_name="Товар",
    )
    operation_type = models.CharField(
        "Тип операции", max_length=10, choices=OperationType.choices
    )
    quantity = models.PositiveIntegerField("Количество")
    operation_date = models.DateField("Дата операции")
    comment = models.CharField("Комментарий", max_length=255, blank=True, default="")
    is_cancelled = models.BooleanField("Отменена", default=False)

    class Meta:
        ordering = ["-operation_date", "-pk"]
        verbose_name = "Складская операция"
        verbose_name_plural = "Складские операции"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="operation_quantity_positive",
            ),
        ]

    @property
    def status(self) -> OperationStatus:
        """Текстовый статус, вычисляемый из существующего флага отмены."""
        return OperationStatus.CANCELLED if self.is_cancelled else OperationStatus.ACTIVE

    def __str__(self) -> str:
        action = self.get_operation_type_display()
        return (
            f"{action} {self.quantity} {self.product.unit} — {self.product.name} "
            f"({self.operation_date:%d.%m.%Y})"
        )

    def cancel(self) -> bool:
        """Пометить операцию отменённой.

        Returns:
            True, если операция отменена сейчас, False — если уже была отменена.
        """
        if self.is_cancelled:
            return False
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])
        return True
