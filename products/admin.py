from django.contrib import admin

from products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "article", "category", "price", "stock", "total_value")
    search_fields = ("name", "article")
    list_filter = ("category",)
    list_per_page = 25
    ordering = ("name",)
    readonly_fields = ("total_value",)
