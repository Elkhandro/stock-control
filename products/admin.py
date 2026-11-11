from django.contrib import admin

from products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "article", "category", "price", "stock")
    search_fields = ("name", "article")
    list_filter = ("category",)
