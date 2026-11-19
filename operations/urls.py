"""Маршруты приложения operations."""

from django.urls import path

from . import views

app_name = "operations"

urlpatterns = [
    # SQLite-версии (основные для ПР7)
    path("", views.operation_list, name="operation_list"),
    path("statistics/", views.operation_statistics, name="operation_statistics"),
    path("new/", views.operation_create, name="operation_create"),
    path("<int:pk>/edit/", views.operation_edit, name="operation_edit"),
    path("<int:pk>/cancel/", views.operation_cancel, name="operation_cancel"),
    path("<int:pk>/", views.operation_detail, name="operation_detail"),

    # Формы прихода/расхода (работают через JSON, запись в БД не требуется по ПР7)
    path("receive/", views.operation_receive, name="operation_receive"),
    path("ship/", views.operation_ship, name="operation_ship"),

    # JSON-версии (сохранены, доступны по отдельным URL)
    path("json/", views.operation_list_json, name="operation_list_json"),
    path("json/<int:operation_id>/", views.operation_detail_json, name="operation_detail_json"),
]
