"""Glue between Django models and the pure packing engine."""
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from . import packing
from .models import Order, OrderItem, Product, ShippingBox


def _q(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01")))


def build_items(order_lines):
    """order_lines: [{'product_id':int,'quantity':int}] -> (list[Item], {id: Product})."""
    products = Product.objects.in_bulk([l["product_id"] for l in order_lines])
    items = []
    for line in sorted(order_lines, key=lambda l: l["product_id"]):
        p = products[line["product_id"]]
        for n in range(line["quantity"]):
            label = p.name if line["quantity"] == 1 else f"{p.name} #{n + 1}"
            items.append(packing.Item(p.id, label, p.length, p.width, p.height, p.weight))
    return items, products


def _box_spec(b: ShippingBox) -> packing.BoxSpec:
    return packing.BoxSpec(b.id, b.name, b.inner_length, b.inner_width, b.inner_height,
                           b.max_weight, b.cost)


def _eval_dict(ev: packing.BoxEvaluation, rec_total_weight, rec_total_volume):
    b = ev.box
    d = {
        "box_id": b.id, "box_name": b.name, "cost_inr": _q(b.cost),
        "status": ev.result.status.value, "reason": ev.result.reason,
        "nodes_explored": ev.result.nodes_explored,
    }
    if ev.result.status == packing.PackStatus.FEASIBLE:
        d["remaining_weight_capacity_kg"] = _q(b.max_weight - rec_total_weight)
        d["space_utilization_percent"] = _q(rec_total_volume / b.volume * 100)
    return d


def run_recommendation(order_lines, persist=True):
    items, products = build_items(order_lines)
    rec = packing.recommend(items, [_box_spec(b) for b in ShippingBox.objects.all()],
                            settings.PACKING_MAX_NODES, settings.PACKING_MAX_SECONDS)
    response = {
        "status": rec.status,
        "message": rec.message,
        "units": "dimensions in cm, weight in kg, cost in INR",
        "items": [{"product_id": l["product_id"], "name": products[l["product_id"]].name,
                   "quantity": l["quantity"]} for l in order_lines],
        "total_weight_kg": _q(rec.total_weight),
        "total_volume_cm3": _q(rec.total_volume),
        "cheaper_rejections_all_proven": rec.cheaper_rejections_all_proven,
        "search_limits": {"max_nodes": settings.PACKING_MAX_NODES,
                          "max_seconds": settings.PACKING_MAX_SECONDS},
        "algorithm_note": ("Backtracking search over axis-aligned rotations and candidate "
                           "positions. Heuristic: not a proof of global optimality."),
        "box": None, "placements": [], "validation": None, "other_suitable_boxes": [],
        "boxes_evaluated": [_eval_dict(e, rec.total_weight, rec.total_volume)
                            for e in rec.evaluations],
    }
    chosen_box = None
    if rec.chosen:
        b = rec.chosen.box
        chosen_box = ShippingBox.objects.get(pk=b.id)
        errors = packing.validate_arrangement(items, b, rec.chosen.result.placements)
        response["box"] = {
            "id": b.id, "name": b.name, "code": chosen_box.code,
            "inner_dimensions_cm": {"length": _q(b.length), "width": _q(b.width),
                                    "height": _q(b.height)},
            "max_weight_kg": _q(b.max_weight), "cost_inr": _q(b.cost),
            "weight_utilization_percent": _q(rec.total_weight / b.max_weight * 100),
            "space_utilization_percent": _q(rec.total_volume / b.volume * 100),
            "remaining_weight_capacity_kg": _q(b.max_weight - rec.total_weight),
        }
        response["placements"] = [{
            "product_id": p.product_id, "name": p.name,
            "position_cm": {"x": _q(p.x), "y": _q(p.y), "z": _q(p.z)},
            "placed_size_cm": {"length": _q(p.length), "width": _q(p.width), "height": _q(p.height)},
            "weight_kg": _q(p.weight)} for p in rec.chosen.result.placements]
        response["validation"] = {"valid": not errors, "errors": errors,
                                  "checks": ["inside box", "non-negative coordinates",
                                             "no overlaps", "weight within capacity"]}
        response["other_suitable_boxes"] = [
            _eval_dict(e, rec.total_weight, rec.total_volume) for e in rec.evaluations
            if e.result.status == packing.PackStatus.FEASIBLE and e is not rec.chosen]

    if persist:
        with transaction.atomic():
            order = Order.objects.create(status=rec.status, box=chosen_box,
                                         total_weight=rec.total_weight, result=response)
            OrderItem.objects.bulk_create([
                OrderItem(order=order, product_id=l["product_id"], quantity=l["quantity"])
                for l in order_lines])
        response["order_id"] = order.id
    return response
