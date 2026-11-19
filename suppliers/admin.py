from django.contrib import admin

from suppliers.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone", "email", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_person", "phone", "email")
    readonly_fields = ("created_at",)
    list_per_page = 25
