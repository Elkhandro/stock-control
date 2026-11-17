from django.contrib import admin
from django.utils import timezone

from operations.models import Operation, OperationStatus


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "product", "operation_type", "quantity", "operation_date",
        "status",
    )
    list_filter = ("operation_type", "status", "operation_date")
    search_fields = ("product__name", "product__article", "comment")
    autocomplete_fields = ("product",)
    list_select_related = ("product",)
    date_hierarchy = "operation_date"
    ordering = ("-operation_date", "-pk")
    list_per_page = 25
    list_editable = ("status",)
    actions = ("cancel_operations", "complete_operations", "restore_operations")

    @admin.action(description="Отменить выбранные операции")
    def cancel_operations(self, request, queryset):
        updated = queryset.exclude(status=OperationStatus.CANCELLED).update(
            status=OperationStatus.CANCELLED
        )
        self.message_user(request, f"Отменено операций: {updated}")

    @admin.action(description="Завершить выбранные операции")
    def complete_operations(self, request, queryset):
        updated = queryset.exclude(status=OperationStatus.COMPLETED).update(
            status=OperationStatus.COMPLETED
        )
        self.message_user(request, f"Завершено операций: {updated}")

    @admin.action(description="Вернуть выбранные операции в активные")
    def restore_operations(self, request, queryset):
        updated = queryset.exclude(status=OperationStatus.ACTIVE).update(
            status=OperationStatus.ACTIVE
        )
        self.message_user(request, f"Возвращено в активные: {updated}")
