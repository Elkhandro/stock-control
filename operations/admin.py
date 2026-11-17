from django.contrib import admin

from operations.models import Operation


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "product", "operation_type", "quantity", "operation_date", "status",
    )
    list_filter = ("operation_type", "status")
    search_fields = ("product__name", "product__article", "comment")
    list_select_related = ("product",)
    date_hierarchy = "operation_date"
    ordering = ("-operation_date", "-pk")
    list_per_page = 25
