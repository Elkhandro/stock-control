"""Маршруты приложения operations."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.operation_list, name="operation_list"),
    path("receive/", views.operation_receive, name="operation_receive"),
    path("ship/", views.operation_ship, name="operation_ship"),
    path("<int:operation_id>/", views.operation_detail, name="operation_detail"),
]