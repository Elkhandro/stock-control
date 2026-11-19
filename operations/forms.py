from django import forms
from django.utils import timezone

from operations.models import Operation, OperationStatus, OperationType
from products.models import Product


class OperationFilterForm(forms.Form):
    date = forms.DateField(
        required=False, label="Дата",
        error_messages={"invalid": "Укажите корректную дату."},
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    product = forms.ModelChoiceField(
        required=False, label="Товар", queryset=Product.objects.order_by("name"),
        empty_label="Все товары",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    type = forms.ChoiceField(
        required=False, label="Тип операции",
        choices=[("", "Любой тип"), *OperationType.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        required=False, label="Статус",
        choices=[("active", "Активные"), ("cancelled", "Отменённые"),
                 ("completed", "Завершённые"), ("all", "Все")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        required=False, label="Сортировка",
        choices=[("date", "Сначала новые"), ("date_asc", "Сначала старые"),
                 ("product", "По товару"), ("type", "По типу")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = ("product", "operation_type", "quantity", "operation_date", "comment")
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "operation_type": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "operation_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "comment": forms.TextInput(attrs={"class": "form-control", "maxlength": "255"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.order_by("name")
        if not self.is_bound and not self.instance.pk:
            self.initial.setdefault("operation_date", timezone.localdate())

    def clean_operation_date(self):
        operation_date = self.cleaned_data["operation_date"]
        if operation_date < timezone.localdate():
            original_date = self.instance.operation_date if self.instance.pk else None
            if operation_date != original_date:
                raise forms.ValidationError("Нельзя указать дату новой операции в прошлом.")
        return operation_date

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        operation_type = cleaned.get("operation_type")
        quantity = cleaned.get("quantity")
        if not all((product, operation_type, quantity)):
            return cleaned

        available_stock = product.stock
        current = self.instance
        if current.pk and current.status == OperationStatus.ACTIVE and current.product_id == product.pk:
            if current.operation_type == OperationType.ISSUE:
                available_stock += current.quantity
            elif current.operation_type == OperationType.RECEIPT:
                available_stock -= current.quantity

        if operation_type == OperationType.ISSUE and quantity > available_stock:
            self.add_error(None, f"Недостаточно товара на складе. Доступно: {max(available_stock, 0)}.")
        return cleaned
