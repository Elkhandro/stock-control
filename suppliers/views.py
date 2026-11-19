from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from suppliers.forms import SupplierForm
from suppliers.models import Supplier


def supplier_list(request):
    suppliers = Supplier.objects.filter(is_active=True).prefetch_related("products")
    return render(request, "suppliers/supplier_list.html", {"suppliers": suppliers})


@require_http_methods(["GET", "POST"])
def supplier_create(request):
    form = SupplierForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        supplier = form.save()
        messages.success(request, "Поставщик добавлен.")
        return redirect("suppliers:supplier_list")
    return render(request, "suppliers/supplier_form.html", {"form": form, "object": None})


@require_http_methods(["GET", "POST"])
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, request.FILES or None, instance=supplier)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Данные поставщика обновлены.")
        return redirect("suppliers:supplier_list")
    return render(request, "suppliers/supplier_form.html", {"form": form, "object": supplier})


@require_POST
def supplier_deactivate(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk, is_active=True)
    supplier.is_active = False
    supplier.save(update_fields=["is_active"])
    messages.success(request, "Поставщик деактивирован. История товаров сохранена.")
    return redirect("suppliers:supplier_list")
