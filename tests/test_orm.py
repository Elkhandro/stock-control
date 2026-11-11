"""Тесты ORM-моделей и представлений (ПР9)."""

from datetime import date
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from operations.models import ISSUE, RECEIPT, Operation
from products.models import Product


def make_product(article="NB-001", name="Ноутбук Lenovo", category="Электроника",
                 price="75000.50", stock=15):
    return Product.objects.create(
        name=name, article=article, category=category,
        unit="шт.", price=Decimal(price), stock=stock,
    )


def make_operation(product, op_type=RECEIPT, quantity=10, day=15, cancelled=False):
    return Operation.objects.create(
        product=product, operation_type=op_type, quantity=quantity,
        operation_date=date(2026, 9, day), comment="", is_cancelled=cancelled,
    )


class ModelTests(TestCase):
    def test_str_and_total_value(self):
        product = make_product(price="100.50", stock=3)
        self.assertEqual(str(product), "Ноутбук Lenovo")
        self.assertEqual(product.get_total_value(), Decimal("301.50"))

    def test_low_stock_and_availability(self):
        product = make_product(stock=5)
        self.assertTrue(product.is_low_stock())
        self.assertTrue(product.check_availability(5))
        self.assertFalse(product.check_availability(6))

    def test_article_is_unique(self):
        make_product()
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_product(name="Другой")

    def test_operation_cancel(self):
        operation = make_operation(make_product())
        self.assertTrue(operation.cancel())
        operation.refresh_from_db()
        self.assertTrue(operation.is_cancelled)
        self.assertFalse(operation.cancel())

    def test_quantity_must_be_positive(self):
        product = make_product()
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_operation(product, quantity=0)

    def test_protect_on_delete(self):
        product = make_product()
        make_operation(product)
        with self.assertRaises(ProtectedError):
            product.delete()

    def test_related_name(self):
        product = make_product()
        make_operation(product)
        make_operation(product, ISSUE, 2, day=16)
        self.assertEqual(product.operations.count(), 2)


class QueryTests(TestCase):
    def setUp(self):
        self.laptop = make_product()
        self.mouse = make_product("MS-004", "Мышь Defender", "Периферия", "1200", 5)
        self.cable = make_product("CB-005", "Кабель HDMI", "Аксессуары", "450", 100)
        make_operation(self.laptop, RECEIPT, 10, day=15, cancelled=True)
        make_operation(self.laptop, ISSUE, 2, day=16)
        make_operation(self.mouse, RECEIPT, 7, day=17)

    def test_summary(self):
        summary = Product.objects.summary()
        self.assertEqual(summary["total_products"], 3)
        self.assertEqual(summary["total_units"], 120)
        self.assertEqual(
            summary["total_value"], Decimal("75000.50") * 15 + 1200 * 5 + 450 * 100
        )

    def test_summary_empty(self):
        Operation.objects.all().delete()
        Product.objects.all().delete()
        summary = Product.objects.summary()
        self.assertEqual(summary["total_products"], 0)
        self.assertIsNone(summary["total_value"])

    def test_cyrillic_search_is_case_insensitive(self):
        self.assertEqual(list(Product.objects.filter(name__icontains="ноутбук")), [self.laptop])
        self.assertEqual(Product.objects.filter(category__iexact="периферия").count(), 1)
        self.assertEqual(Product.objects.filter(article__istartswith="nb").count(), 1)

    def test_like_wildcards_are_escaped(self):
        self.assertEqual(Product.objects.filter(name__icontains="%").count(), 0)
        self.assertEqual(Product.objects.filter(name__icontains="_").count(), 0)

    def test_filter_by_related_field(self):
        ops = Operation.objects.filter(product__category="Периферия")
        self.assertEqual(ops.count(), 1)

    def test_exclude_products_with_active_operations(self):
        active_ids = Operation.objects.filter(is_cancelled=False).values_list(
            "product_id", flat=True
        )
        idle = Product.objects.exclude(pk__in=active_ids)
        self.assertEqual(list(idle), [self.cable])

    def test_annotate_count_keeps_products_without_operations(self):
        from django.db.models import Count, Q

        stats = {
            row["name"]: row["operations_count"]
            for row in Product.objects.annotate(
                operations_count=Count("operations", filter=Q(operations__is_cancelled=False))
            ).values("name", "operations_count")
        }
        self.assertEqual(stats, {"Ноутбук Lenovo": 1, "Мышь Defender": 1, "Кабель HDMI": 0})

    def test_select_related_single_query(self):
        with self.assertNumQueries(1):
            names = [op.product.name for op in Operation.objects.select_related("product")]
        self.assertEqual(len(names), 3)


class ViewTests(TestCase):
    def setUp(self):
        self.laptop = make_product()
        self.mouse = make_product("MS-004", "Мышь Defender", "Периферия", "1200", 5)
        self.cable = make_product("CB-005", "Кабель HDMI", "Аксессуары", "450", 100)
        self.cancelled = make_operation(self.laptop, RECEIPT, 10, day=15, cancelled=True)
        self.op2 = make_operation(self.laptop, ISSUE, 2, day=16)
        self.op3 = make_operation(self.mouse, RECEIPT, 7, day=17)

    def test_all_pages_ok(self):
        for name, args in [
            ("homepage:index", []),
            ("products:product_list", []),
            ("products:product_search", []),
            ("products:product_detail", [self.laptop.pk]),
            ("operations:operation_list", []),
            ("operations:operation_detail", [self.op2.pk]),
            ("operations:operation_statistics", []),
        ]:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200)

    def test_404_via_get_object_or_404(self):
        for name in ("products:product_detail", "operations:operation_detail"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=[999999]))
                self.assertEqual(response.status_code, 404)

    def test_homepage_low_stock_and_counts(self):
        response = self.client.get(reverse("homepage:index"))
        self.assertEqual(response.context["active_operations_count"], 2)
        self.assertEqual(list(response.context["low_stock_products"]), [self.mouse])

    def test_product_list_search_and_sort(self):
        url = reverse("products:product_list")
        response = self.client.get(url, {"q": "ноут"})
        self.assertEqual(list(response.context["products"]), [self.laptop])
        response = self.client.get(url, {"sort": "stock_desc"})
        self.assertEqual(list(response.context["products"]), [self.cable, self.laptop, self.mouse])
        response = self.client.get(url, {"sort": "'; DROP TABLE"})
        self.assertEqual(response.context["sort"], "name")

    def test_product_search_filters(self):
        url = reverse("products:product_search")
        self.assertEqual(self.client.get(url).context["searched"], False)
        response = self.client.get(url, {"max_stock": "10"})
        self.assertEqual(list(response.context["products"]), [self.mouse])
        response = self.client.get(url, {"category": "электроника"})
        self.assertEqual(list(response.context["products"]), [self.laptop])
        response = self.client.get(url, {"max_stock": "abc"})
        self.assertEqual(response.status_code, 200)

    def test_operation_list_defaults_to_active_only(self):
        response = self.client.get(reverse("operations:operation_list"))
        ids = [op["id"] for op in response.context["operations"]]
        self.assertEqual(ids, [self.op3.pk, self.op2.pk])

    def test_operation_list_filters(self):
        url = reverse("operations:operation_list")
        r = self.client.get(url, {"status": "all"})
        self.assertEqual(len(r.context["operations"]), 3)
        r = self.client.get(url, {"status": "cancelled"})
        self.assertEqual([op["id"] for op in r.context["operations"]], [self.cancelled.pk])
        r = self.client.get(url, {"product": str(self.mouse.pk)})
        self.assertEqual([op["id"] for op in r.context["operations"]], [self.op3.pk])
        r = self.client.get(url, {"type": "расход"})
        self.assertEqual([op["id"] for op in r.context["operations"]], [self.op2.pk])
        r = self.client.get(url, {"date": "2026-09-16"})
        self.assertEqual([op["id"] for op in r.context["operations"]], [self.op2.pk])
        # несколько условий — «И»
        r = self.client.get(url, {"product": str(self.laptop.pk), "type": "приход"})
        self.assertEqual(len(r.context["operations"]), 0)

    def test_operation_list_bad_params_do_not_crash(self):
        url = reverse("operations:operation_list")
        r = self.client.get(url, {"date": "31.02.2026"})
        self.assertEqual(r.context["error"], "Укажите корректную дату.")
        self.assertEqual(len(r.context["operations"]), 2)
        for params in ({"product": "9" * 30}, {"product": "²"}, {"type": "x"},
                       {"sort": "evil"}, {"status": "evil"}, {"page": "abc"}, {"page": "99"}):
            with self.subTest(params=params):
                self.assertEqual(self.client.get(url, params).status_code, 200)

    def test_operation_list_sort(self):
        url = reverse("operations:operation_list")
        r = self.client.get(url, {"sort": "product", "status": "all"})
        names = [op["product_name"] for op in r.context["operations"]]
        self.assertEqual(names, sorted(names))
        r = self.client.get(url, {"sort": "date_asc", "status": "all"})
        dates = [op["operation_date"] for op in r.context["operations"]]
        self.assertEqual(dates, sorted(dates))

    def test_pagination_keeps_filters(self):
        for i in range(7):
            make_operation(self.cable, ISSUE, 1, day=18 + i)
        url = reverse("operations:operation_list")
        r = self.client.get(url, {"type": "расход", "page": "2"})
        self.assertEqual(r.context["page_obj"].number, 2)
        self.assertEqual(r.context["page_obj"].paginator.num_pages, 2)
        self.assertContains(r, "type=%D1%80%D0%B0%D1%81%D1%85%D0%BE%D0%B4")
        self.assertEqual(self.client.get(url, {"page": "abc"}).context["page_obj"].number, 1)

    def test_statistics_excludes_cancelled_and_keeps_idle_products(self):
        r = self.client.get(reverse("operations:operation_statistics"))
        counts = {row["name"]: row["operations_count"] for row in r.context["product_stats"]}
        self.assertEqual(counts["Ноутбук Lenovo"], 1)  # отменённая не считается
        self.assertEqual(counts["Кабель HDMI"], 0)  # товар без операций не выпал
        self.assertEqual(list(r.context["idle_products"]), [self.cable])
        types = {row["operation_type"]: row["total_quantity"] for row in r.context["type_stats"]}
        self.assertEqual(types, {RECEIPT: 7, ISSUE: 2})

    def test_statistics_on_empty_database(self):
        Operation.objects.all().delete()
        Product.objects.all().delete()
        for name in ("operations:operation_statistics", "homepage:index"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_product_detail_shows_operations_via_related_manager(self):
        r = self.client.get(reverse("products:product_detail", args=[self.laptop.pk]))
        self.assertEqual(len(r.context["operations"]), 2)
