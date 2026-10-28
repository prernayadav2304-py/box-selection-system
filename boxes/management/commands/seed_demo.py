from django.core.management.base import BaseCommand

from boxes.models import Product, ShippingBox

PRODUCTS = [("DEMO-BOOK", "Demo Book", "20", "15", "5", "2"),
            ("DEMO-MUG", "Demo Mug", "8", "8", "10", "0.5"),
            ("DEMO-LAMP", "Demo Lamp", "30", "12", "12", "1.5")]
BOXES = [("DEMO-S", "Demo Small Box", "25", "20", "15", "5", "40"),
         ("DEMO-M", "Demo Medium Box", "40", "30", "20", "10", "70"),
         ("DEMO-L", "Demo Large Box", "60", "40", "40", "25", "120")]


class Command(BaseCommand):
    help = "Create clearly-labelled DEMO products and boxes (safe to re-run)."

    def handle(self, *args, **opts):
        for sku, name, l, w, h, wt in PRODUCTS:
            Product.objects.get_or_create(sku=sku, defaults=dict(name=name, length=l, width=w, height=h, weight=wt))
        for code, name, l, w, h, mw, cost in BOXES:
            ShippingBox.objects.get_or_create(code=code, defaults=dict(
                name=name, inner_length=l, inner_width=w, inner_height=h, max_weight=mw, cost=cost))
        self.stdout.write(self.style.SUCCESS("Demo data ready."))
