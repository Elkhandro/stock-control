from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html

from operations.models import Operation, OperationStatus
from products.models import Product


class OperationInline(admin.TabularInline):
    model = Operation
    extra = 0
    fields = ("operation_type", "quantity", "operation_date", "status", "comment")
    readonly_fields = ()
    show_change_link = True
    autocomplete_fields = ("product",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "article", "category", "price", "stock",
        "total_value", "active_operations_count", "site_link",
    )
    list_display_links = ("name", "article")
    list_editable = ("stock",)
    search_fields = ("name", "article")
    list_filter = ("category",)
    list_per_page = 25
    ordering = ("name",)
    readonly_fields = ("total_value",)
    inlines = (OperationInline,)

    @admin.display(description="Активных операций", ordering="active_operations_count")
    def active_operations_count(self, obj):
        return obj.active_operations_count

    @admin.display(description="Страница", boolean=False)
    def site_link(self, obj):
        return format_html('<a href="{}">Открыть</a>', obj.get_absolute_url())

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            active_operations_count=Count(
                "operations", filter=Q(operations__status=OperationStatus.ACTIVE)
            )
        )
