from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

POSITIVE = [MinValueValidator(Decimal("0.01"))]


class Product(models.Model):
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=64, unique=True)
    length = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    width = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    height = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    weight = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(length__gt=0, width__gt=0, height__gt=0, weight__gt=0),
                name="product_positive_dims_weight"),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"


class ShippingBox(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=64, unique=True)
    inner_length = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    inner_width = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    inner_height = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    max_weight = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    cost = models.DecimalField(max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(Decimal("0"))])  # INR
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(inner_length__gt=0, inner_width__gt=0, inner_height__gt=0, max_weight__gt=0),
                name="box_positive_dims_weight"),
            models.CheckConstraint(condition=Q(cost__gte=0), name="box_cost_non_negative"),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("recommended", "Recommended"),
        ("no_suitable_box", "No suitable box"),
        ("undetermined", "Undetermined (search limit)"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    box = models.ForeignKey(ShippingBox, null=True, blank=True, on_delete=models.SET_NULL,
                            related_name="orders")
    total_weight = models.DecimalField(max_digits=10, decimal_places=2)
    result = models.JSONField(default=dict)  # full recommendation response snapshot
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gte=1), name="orderitem_qty_positive"),
            models.UniqueConstraint(fields=["order", "product"], name="orderitem_unique_product"),
        ]
