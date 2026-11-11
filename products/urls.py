"""Маршруты приложения products."""

from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    # SQLite-версии (основные для ПР7)
    path("", views.product_list, name="product_list"),
    path("search/", views.product_search, name="product_search"),
    path("add/", views.product_add, name="product_add"),
    path("<int:pk>/", views.product_detail, name="product_detail"),

    # JSON-версии (сохранены, доступны по отдельным URL)
    path("json/", views.product_list_json, name="product_list_json"),
    path("json/<int:product_id>/", views.product_detail_json, name="product_detail_json"),
]
