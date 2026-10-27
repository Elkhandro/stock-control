"""Маршруты приложения operations."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.operation_list, name="operation_list"),
    path("<int:operation_id>/", views.operation_detail, name="operation_detail"),
]