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
    """Состояния складской операции."""

    ACTIVE = "active", "Активна"
    CANCELLED = "cancelled", "Отменена"
    COMPLETED = "completed", "Завершена"


class OperationQuerySet(models.QuerySet):
    """Переиспользуемые выборки операций склада."""

    def active(self):
        return self.filter(status=OperationStatus.ACTIVE)

    def cancelled(self):
        return self.filter(status=OperationStatus.CANCELLED)

    def completed(self):
        return self.filter(status=OperationStatus.COMPLETED)

    def for_date(self, day):
        return self.filter(operation_date=day)


class OperationManager(models.Manager.from_queryset(OperationQuerySet)):
    """Менеджер складских операций."""


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
    quantity = models.PositiveIntegerField("Количество", help_text="Количество единиц в операции; должно быть больше нуля.")
    operation_date = models.DateField("Дата операции")
    comment = models.CharField("Комментарий", max_length=255, blank=True, default="")
    status = models.CharField("Статус", max_length=10, choices=OperationStatus.choices, default=OperationStatus.ACTIVE, db_index=True, help_text="Активна, отменена или завершена.")

    objects = OperationManager()

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
    def is_cancelled(self) -> bool:
        """Совместимость со старыми JSON-шаблонами; в БД хранится status."""
        return self.status == OperationStatus.CANCELLED

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
        if self.status == OperationStatus.CANCELLED:
            return False
        self.status = OperationStatus.CANCELLED
        self.save(update_fields=["status"])
        return True

    def complete(self) -> bool:
        """Пометить операцию завершённой."""
        if self.status == OperationStatus.COMPLETED:
            return False
        self.status = OperationStatus.COMPLETED
        self.save(update_fields=["status"])
        return True
