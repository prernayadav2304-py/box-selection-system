from django.conf import settings
from rest_framework import serializers

from .models import Order, OrderItem, Product, ShippingBox


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "sku", "length", "width", "height", "weight", "created_at"]
        read_only_fields = ["id", "created_at"]


class ShippingBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingBox
        fields = ["id", "name", "code", "inner_length", "inner_width", "inner_height",
                  "max_weight", "cost", "created_at"]
        read_only_fields = ["id", "created_at"]


class RecommendItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class RecommendRequestSerializer(serializers.Serializer):
    items = RecommendItemSerializer(many=True, allow_empty=False)

    def validate_items(self, items):
        ids = [i["product_id"] for i in items]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Duplicate product_id entries are not allowed; combine them using quantity.")
        existing = set(Product.objects.filter(id__in=ids).values_list("id", flat=True))
        missing = sorted(set(ids) - existing)
        if missing:
            raise serializers.ValidationError(f"Unknown product IDs: {missing}")
        units = sum(i["quantity"] for i in items)
        if units > settings.MAX_UNITS_PER_ORDER:
            raise serializers.ValidationError(
                f"Too many units ({units}); the limit is {settings.MAX_UNITS_PER_ORDER}.")
        return items


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    box_name = serializers.CharField(source="box.name", read_only=True, default=None)

    class Meta:
        model = Order
        fields = ["id", "status", "box", "box_name", "total_weight", "items", "result", "created_at"]
