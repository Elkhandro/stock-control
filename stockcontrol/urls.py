"""Корневая маршрутизация Django-проекта stockcontrol."""

from django.contrib import admin
from django.urls import include, path

handler404 = "homepage.views.page_not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("products/", include("products.urls")),
    path("operations/", include("operations.urls")),
]
