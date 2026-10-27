"""Маршруты приложения products."""

from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("add/", views.product_add, name="product_add"),
    path("<int:product_id>/", views.product_detail, name="product_detail"),
]