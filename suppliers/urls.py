from django.urls import path

from suppliers import views

app_name = "suppliers"

urlpatterns = [
    path("", views.supplier_list, name="supplier_list"),
    path("new/", views.supplier_create, name="supplier_create"),
    path("<int:pk>/edit/", views.supplier_edit, name="supplier_edit"),
    path("<int:pk>/deactivate/", views.supplier_deactivate, name="supplier_deactivate"),
]
