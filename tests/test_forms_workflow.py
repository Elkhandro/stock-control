import base64
from datetime import timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from operations.models import Operation, OperationStatus, OperationType
from products.models import Product
from suppliers.models import Supplier


class DjangoFormsWorkflowTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name="ООО Поставщик")
        self.product = Product.objects.create(
            name="Тестовый товар", article="FORM-001", category="Тест",
            supplier=self.supplier, unit="шт.", price=Decimal("10.00"), stock=5,
        )

    def test_operation_filter_form_preserves_selected_filters(self):
        today = timezone.localdate()
        Operation.objects.create(
            product=self.product, operation_type=OperationType.RECEIPT,
            quantity=2, operation_date=today, status=OperationStatus.ACTIVE,
        )
        response = self.client.get(reverse("operations:operation_list"), {
            "date": today.isoformat(), "product": self.product.pk,
            "operation_type": OperationType.RECEIPT, "status": "active", "sort": "date",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["operations"]), 1)
        self.assertTrue(response.context["form"].is_valid())
        self.assertEqual(response.context["form"].cleaned_data["product"], self.product)

    def test_operation_create_receipt_updates_stock(self):
        response = self.client.post(reverse("operations:operation_create"), {
            "product": self.product.pk,
            "operation_type": OperationType.RECEIPT,
            "quantity": 3,
            "operation_date": timezone.localdate().isoformat(),
            "comment": "Поставка",
        })
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        self.assertEqual(Operation.objects.active().count(), 1)

    def test_operation_create_rejects_past_date_and_insufficient_stock(self):
        past = timezone.localdate() - timedelta(days=1)
        response = self.client.post(reverse("operations:operation_create"), {
            "product": self.product.pk,
            "operation_type": OperationType.ISSUE,
            "quantity": 99,
            "operation_date": past.isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("operation_date", response.context["form"].errors)
        self.assertIn("__all__", response.context["form"].errors)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(Operation.objects.count(), 0)

    def test_operation_edit_and_cancel_compensate_stock(self):
        operation = Operation.objects.create(
            product=self.product, operation_type=OperationType.RECEIPT,
            quantity=4, operation_date=timezone.localdate(), status=OperationStatus.ACTIVE,
        )
        self.product.stock += 4
        self.product.save(update_fields=["stock"])
        response = self.client.post(reverse("operations:operation_edit", args=[operation.pk]), {
            "product": self.product.pk,
            "operation_type": OperationType.ISSUE,
            "quantity": 2,
            "operation_date": timezone.localdate().isoformat(),
            "comment": "Изменено",
        })
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        response = self.client.post(reverse("operations:operation_cancel", args=[operation.pk]))
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        operation.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(operation.status, OperationStatus.CANCELLED)

    def test_cancel_requires_post(self):
        operation = Operation.objects.create(
            product=self.product, operation_type=OperationType.RECEIPT,
            quantity=1, operation_date=timezone.localdate(), status=OperationStatus.ACTIVE,
        )
        response = self.client.get(reverse("operations:operation_cancel", args=[operation.pk]))
        self.assertEqual(response.status_code, 405)

    def test_invalid_operation_and_product_ids_return_404(self):
        self.assertEqual(self.client.get(reverse("operations:operation_edit", args=[999999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("operations:operation_detail", args=[999999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("products:product_edit", args=[999999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("suppliers:supplier_edit", args=[999999])).status_code, 404)

    def test_product_image_upload_and_edit(self):
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/pWQAAAAASUVORK5CYII="
        )
        upload = SimpleUploadedFile("item.png", png, content_type="image/png")
        response = self.client.post(reverse("products:product_create"), {
            "name": "Фото товар", "article": "PHOTO-001", "category": "Тест",
            "supplier": self.supplier.pk, "unit": "шт.", "price": "12.50", "stock": "2",
            "image": upload,
        })
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(article="PHOTO-001")
        self.assertTrue(product.image.name.startswith("products/"))
        self.assertEqual(self.client.get(product.get_absolute_url()).status_code, 200)

    def test_supplier_soft_deactivation_preserves_products(self):
        response = self.client.post(reverse("suppliers:supplier_deactivate", args=[self.supplier.pk]))
        self.assertEqual(response.status_code, 302)
        self.supplier.refresh_from_db()
        self.product.refresh_from_db()
        self.assertFalse(self.supplier.is_active)
        self.assertEqual(self.product.supplier, self.supplier)
