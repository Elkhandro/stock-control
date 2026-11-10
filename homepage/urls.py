"""Маршруты приложения homepage."""

from django.urls import path

from . import views

app_name = "homepage"

urlpatterns = [
    # SQLite-версия (основная для ПР7)
    path("", views.index, name="index"),

    # JSON-версия (сохранена)
    path("json/", views.index_json, name="index_json"),
]