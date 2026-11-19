from django import forms

from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "article", "category", "supplier", "unit", "price", "stock", "image")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "article": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "unit": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].queryset = self.fields["supplier"].queryset.filter(is_active=True)
        if self.instance.pk and self.instance.supplier_id:
            self.fields["supplier"].queryset = self.fields["supplier"].queryset | self.fields["supplier"].queryset.model.objects.filter(pk=self.instance.supplier_id)
        self.fields["supplier"].required = False
