"""API / model tests (database-backed)."""
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from boxes.models import Order, Product, ShippingBox


class BaseAPITest(TestCase):
    def setUp(self):
        self.c = APIClient()
        self.book = Product.objects.create(name="Book", sku="BK1", length=20, width=15, height=5, weight=2)
        self.mug = Product.objects.create(name="Mug", sku="MG1", length=8, width=8, height=10, weight=0.5)
        self.small = ShippingBox.objects.create(name="Small", code="S", inner_length=25, inner_width=20,
                                                inner_height=15, max_weight=5, cost=40)
        self.large = ShippingBox.objects.create(name="Large", code="L", inner_length=40, inner_width=30,
                                                inner_height=20, max_weight=10, cost=70)

    def rec(self, items):
        return self.c.post("/api/recommend/", {"items": items}, format="json")


class ProductAPITests(BaseAPITest):
    payload = {"name": "Plate", "sku": "PL1", "length": "15", "width": "15", "height": "2", "weight": "0.4"}

    def test_create_and_list(self):
        self.assertEqual(self.c.post("/api/products/", self.payload, format="json").status_code, 201)
        r = self.c.get("/api/products/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 3)

    def test_zero_dimension_rejected(self):
        self.assertEqual(self.c.post("/api/products/", {**self.payload, "length": "0"}, format="json").status_code, 400)

    def test_negative_dimension_rejected(self):
        self.assertEqual(self.c.post("/api/products/", {**self.payload, "height": "-3"}, format="json").status_code, 400)

    def test_negative_weight_rejected(self):
        self.assertEqual(self.c.post("/api/products/", {**self.payload, "weight": "-1"}, format="json").status_code, 400)

    def test_missing_dimension_rejected(self):
        p = dict(self.payload); del p["width"]
        r = self.c.post("/api/products/", p, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("width", r.data)

    def test_non_numeric_rejected(self):
        self.assertEqual(self.c.post("/api/products/", {**self.payload, "length": "abc"}, format="json").status_code, 400)

    def test_duplicate_sku_rejected(self):
        self.assertEqual(self.c.post("/api/products/", {**self.payload, "sku": "BK1"}, format="json").status_code, 400)

    def test_update_and_delete(self):
        r = self.c.patch(f"/api/products/{self.mug.id}/", {"weight": "0.7"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.c.delete(f"/api/products/{self.mug.id}/").status_code, 204)

    def test_cannot_delete_product_used_in_order(self):
        self.rec([{"product_id": self.book.id, "quantity": 1}])
        self.assertEqual(self.c.delete(f"/api/products/{self.book.id}/").status_code, 409)

    def test_db_constraint_blocks_zero(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.create(name="Bad", sku="BAD", length=0, width=1, height=1, weight=1)


class BoxAPITests(BaseAPITest):
    payload = {"name": "XL", "code": "XL", "inner_length": "80", "inner_width": "60",
               "inner_height": "50", "max_weight": "30", "cost": "200"}

    def test_create(self):
        self.assertEqual(self.c.post("/api/boxes/", self.payload, format="json").status_code, 201)

    def test_invalid_values_rejected(self):
        for field, val in [("inner_length", "0"), ("max_weight", "-5"), ("cost", "-1")]:
            r = self.c.post("/api/boxes/", {**self.payload, field: val}, format="json")
            self.assertEqual(r.status_code, 400, field)

    def test_duplicate_code_rejected(self):
        self.assertEqual(self.c.post("/api/boxes/", {**self.payload, "code": "S"}, format="json").status_code, 400)


class RecommendAPITests(BaseAPITest):
    def test_single_product_cheapest_box(self):
        r = self.rec([{"product_id": self.book.id, "quantity": 1}])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "recommended")
        self.assertEqual(r.data["box"]["id"], self.small.id)
        self.assertTrue(r.data["validation"]["valid"])
        self.assertEqual(len(r.data["other_suitable_boxes"]), 1)

    def test_quantity_counts_weight_and_placements(self):
        r = self.rec([{"product_id": self.book.id, "quantity": 2}])  # 4 kg
        self.assertEqual(r.data["total_weight_kg"], "4.00")
        self.assertEqual(len(r.data["placements"]), 2)

    def test_quantity_pushes_to_bigger_box_by_weight(self):
        r = self.rec([{"product_id": self.book.id, "quantity": 3}])  # 6 kg > small 5
        self.assertEqual(r.data["box"]["id"], self.large.id)
        rejected = [e for e in r.data["boxes_evaluated"] if e["box_id"] == self.small.id][0]
        self.assertEqual(rejected["status"], "infeasible_proven")

    def test_multiple_products(self):
        r = self.rec([{"product_id": self.book.id, "quantity": 1}, {"product_id": self.mug.id, "quantity": 2}])
        self.assertEqual(r.data["status"], "recommended")
        self.assertEqual(len(r.data["placements"]), 3)

    def test_no_suitable_box(self):
        big = Product.objects.create(name="Fridge", sku="FR", length=200, width=100, height=100, weight=1)
        r = self.rec([{"product_id": big.id, "quantity": 1}])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "no_suitable_box")
        self.assertIsNone(r.data["box"])

    def test_empty_order_rejected(self):
        self.assertEqual(self.rec([]).status_code, 400)

    def test_missing_items_key_rejected(self):
        self.assertEqual(self.c.post("/api/recommend/", {}, format="json").status_code, 400)

    def test_duplicate_product_ids_rejected(self):
        r = self.rec([{"product_id": self.book.id, "quantity": 1}, {"product_id": self.book.id, "quantity": 1}])
        self.assertEqual(r.status_code, 400)

    def test_zero_and_negative_quantity_rejected(self):
        self.assertEqual(self.rec([{"product_id": self.book.id, "quantity": 0}]).status_code, 400)
        self.assertEqual(self.rec([{"product_id": self.book.id, "quantity": -2}]).status_code, 400)

    def test_unknown_product_rejected(self):
        self.assertEqual(self.rec([{"product_id": 99999, "quantity": 1}]).status_code, 400)

    def test_too_many_units_rejected(self):
        self.assertEqual(self.rec([{"product_id": self.mug.id, "quantity": 500}]).status_code, 400)

    def test_order_persisted_and_listed(self):
        r = self.rec([{"product_id": self.book.id, "quantity": 1}])
        self.assertEqual(Order.objects.count(), 1)
        o = self.c.get(f"/api/orders/{r.data['order_id']}/")
        self.assertEqual(o.status_code, 200)
        self.assertEqual(o.data["items"][0]["quantity"], 1)
        self.assertEqual(o.data["result"]["status"], "recommended")

    def test_invalid_request_does_not_create_order(self):
        self.rec([])
        self.assertEqual(Order.objects.count(), 0)

    def test_individually_fit_but_not_together_goes_to_bigger_box(self):
        cube = Product.objects.create(name="Cube", sku="CUBE", length=6, width=6, height=6, weight=1)
        ShippingBox.objects.all().delete()
        ShippingBox.objects.create(name="Tight", code="T", inner_length=10, inner_width=10, inner_height=10,
                                   max_weight=50, cost=10)
        ShippingBox.objects.create(name="Roomy", code="R", inner_length=12, inner_width=12, inner_height=12,
                                   max_weight=50, cost=30)
        r = self.rec([{"product_id": cube.id, "quantity": 2}])
        self.assertEqual(r.data["box"]["code"], "R")
        self.assertFalse(r.data["cheaper_rejections_all_proven"])

    def test_returned_placements_are_inside_box(self):
        r = self.rec([{"product_id": self.book.id, "quantity": 1}, {"product_id": self.mug.id, "quantity": 3}])
        d = r.data["box"]["inner_dimensions_cm"]
        for p in r.data["placements"]:
            self.assertLessEqual(Decimal(p["position_cm"]["x"]) + Decimal(p["placed_size_cm"]["length"]), Decimal(d["length"]))
            self.assertLessEqual(Decimal(p["position_cm"]["y"]) + Decimal(p["placed_size_cm"]["width"]), Decimal(d["width"]))
            self.assertLessEqual(Decimal(p["position_cm"]["z"]) + Decimal(p["placed_size_cm"]["height"]), Decimal(d["height"]))

    def test_health_and_dashboard(self):
        self.assertEqual(self.c.get("/api/health/").data, {"status": "ok"})
        self.assertEqual(self.c.get("/").status_code, 200)
