"""Корневая маршрутизация Django-проекта stockcontrol."""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

handler404 = "homepage.views.page_not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("products/", include("products.urls")),
    path("suppliers/", include("suppliers.urls")),
    path("operations/", include("operations.urls")),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
