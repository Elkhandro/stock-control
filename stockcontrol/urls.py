"""Корневая маршрутизация Django-проекта stockcontrol."""

from django.contrib import admin
from django.urls import include, path

from homepage.views import page_not_found

handler404 = "homepage.views.page_not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("products/", include("products.urls")),
    path("operations/", include("operations.urls")),
]