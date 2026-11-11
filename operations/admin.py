from django.contrib import admin

from operations.models import Operation


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "product", "operation_type", "quantity", "operation_date", "is_cancelled",
    )
    list_filter = ("operation_type", "is_cancelled")
    search_fields = ("product__name", "comment")
