from django import forms

from suppliers.models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ("name", "contact_person", "phone", "email", "address", "notes", "image")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }
