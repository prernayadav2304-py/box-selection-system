from django.contrib import admin

from .models import Order, OrderItem, Product, ShippingBox

admin.site.register(Product)
admin.site.register(ShippingBox)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "box", "total_weight", "created_at")
    inlines = [OrderItemInline]
