"""Unit tests for the pure packing engine (no database)."""
import random
from decimal import Decimal as D

from django.test import SimpleTestCase

from boxes.packing import (BoxSpec, Item, PackStatus, Placement, pack, recommend,
                           validate_arrangement)


def item(name, l, w, h, wt="1", pid=1):
    return Item(pid, name, D(str(l)), D(str(w)), D(str(h)), D(str(wt)))


def box(id, l, w, h, mw="100", cost="10", name=None):
    return BoxSpec(id, name or f"B{id}", D(str(l)), D(str(w)), D(str(h)), D(str(mw)), D(str(cost)))


class SinglePackingTests(SimpleTestCase):
    def test_single_item_fits(self):
        r = pack([item("a", 20, 15, 10, 2)], box(1, 25, 20, 15, 5))
        self.assertEqual(r.status, PackStatus.FEASIBLE)
        self.assertEqual(r.validation_errors, [])

    def test_rotation_needed(self):
        # 30 long item only fits in the 30 cm axis (box is 10 x 30 x 10)
        r = pack([item("long", 30, 5, 5)], box(1, 10, 30, 10))
        self.assertEqual(r.status, PackStatus.FEASIBLE)
        self.assertEqual(r.placements[0].width, D("30"))

    def test_exact_boundary_fit(self):
        r = pack([item("a", 10, 20, 30)], box(1, 30, 20, 10))
        self.assertEqual(r.status, PackStatus.FEASIBLE)

    def test_one_millimetre_too_big_rejected_with_proof(self):
        r = pack([item("a", 10.01, 20, 30)], box(1, 30, 20, 10))
        self.assertEqual(r.status, PackStatus.INFEASIBLE_PROVEN)

    def test_item_larger_than_box_rejected(self):
        r = pack([item("big", 100, 100, 100)], box(1, 25, 20, 15))
        self.assertEqual(r.status, PackStatus.INFEASIBLE_PROVEN)

    def test_weight_exceeded_rejected(self):
        r = pack([item("heavy", 5, 5, 5, 6)], box(1, 25, 20, 15, mw=5))
        self.assertEqual(r.status, PackStatus.INFEASIBLE_PROVEN)
        self.assertIn("weight", r.reason.lower())

    def test_weight_exactly_at_capacity_is_allowed(self):
        r = pack([item("a", 5, 5, 5, 5)], box(1, 25, 20, 15, mw=5))
        self.assertEqual(r.status, PackStatus.FEASIBLE)

    def test_empty_items_not_feasible(self):
        self.assertEqual(pack([], box(1, 5, 5, 5)).status, PackStatus.INFEASIBLE_PROVEN)

    def test_decimal_precision_no_float_error(self):
        # 0.1 + 0.2 == 0.3 exactly with Decimal
        r = pack([item("a", 0.1, 1, 1, "0.1", 1), item("b", 0.2, 1, 1, "0.2", 2)],
                 box(1, 1, 1, 1, mw="0.3"))
        self.assertEqual(r.status, PackStatus.FEASIBLE)


class MultiItemPackingTests(SimpleTestCase):
    def test_two_items_side_by_side(self):
        r = pack([item("a", 10, 10, 10, pid=1), item("b", 10, 10, 10, pid=2)], box(1, 20, 10, 10))
        self.assertEqual(r.status, PackStatus.FEASIBLE)
        self.assertEqual(validate_arrangement(
            [item("a", 10, 10, 10, pid=1), item("b", 10, 10, 10, pid=2)], box(1, 20, 10, 10), r.placements), [])

    def test_eight_cubes_exact_fill(self):
        items = [item("cube", 5, 5, 5, pid=1)] * 8
        r = pack(items, box(1, 10, 10, 10))
        self.assertEqual(r.status, PackStatus.FEASIBLE)
        self.assertEqual(len(r.placements), 8)

    def test_individually_fit_but_not_together(self):
        # two 6cm cubes: each fits a 10cm cube box, volume 432 < 1000, but cannot co-exist
        items = [item("c", 6, 6, 6, pid=1)] * 2
        r = pack(items, box(1, 10, 10, 10))
        self.assertEqual(r.status, PackStatus.INFEASIBLE_SEARCH_EXHAUSTED)

    def test_total_volume_too_large_proven(self):
        items = [item("c", 6, 6, 6, pid=1)] * 5
        r = pack(items, box(1, 10, 10, 10))
        self.assertEqual(r.status, PackStatus.INFEASIBLE_PROVEN)

    def test_needs_backtracking_arrangement(self):
        # 3 slabs 10x10x4 stack to 12 in a 10x10x12 box; orientation choices matter
        items = [item("s", 10, 4, 10, pid=1)] * 3
        r = pack(items, box(1, 10, 10, 12))
        self.assertEqual(r.status, PackStatus.FEASIBLE)

    def test_search_limit_reports_unknown_not_feasible(self):
        items = [item("c", 6, 6, 6, pid=1)] * 2
        r = pack(items, box(1, 10, 10, 10), max_nodes=3)
        self.assertEqual(r.status, PackStatus.UNKNOWN_LIMIT_REACHED)
        self.assertEqual(r.placements, [])

    def test_random_feasible_results_always_validate(self):
        rng = random.Random(42)
        for _ in range(60):
            items = [item(f"i{n}", rng.randint(1, 6), rng.randint(1, 6), rng.randint(1, 6),
                          rng.randint(1, 3), pid=n) for n in range(rng.randint(1, 5))]
            b = box(1, 10, 10, 10, mw="100")
            r = pack(items, b, max_nodes=20000, max_seconds=2)
            if r.status == PackStatus.FEASIBLE:
                self.assertEqual(validate_arrangement(items, b, r.placements), [])


class ValidatorTests(SimpleTestCase):
    def setUp(self):
        self.b = box(1, 10, 10, 10, mw="10")
        self.items = [item("a", 5, 5, 5, 1, 1), item("b", 5, 5, 5, 1, 2)]

    def P(self, pid, name, x, y, z, l=5, w=5, h=5, wt=1):
        return Placement(pid, name, D(x), D(y), D(z), D(l), D(w), D(h), D(wt))

    def test_valid(self):
        pl = [self.P(1, "a", 0, 0, 0), self.P(2, "b", 5, 0, 0)]
        self.assertEqual(validate_arrangement(self.items, self.b, pl), [])

    def test_detects_overlap(self):
        pl = [self.P(1, "a", 0, 0, 0), self.P(2, "b", 4, 0, 0)]
        self.assertTrue(any("overlaps" in e for e in validate_arrangement(self.items, self.b, pl)))

    def test_detects_outside_box(self):
        pl = [self.P(1, "a", 0, 0, 0), self.P(2, "b", 6, 0, 0)]
        self.assertTrue(any("outside" in e for e in validate_arrangement(self.items, self.b, pl)))

    def test_detects_negative_coordinate(self):
        pl = [self.P(1, "a", -1, 0, 0), self.P(2, "b", 5, 0, 0)]
        self.assertTrue(any("negative" in e for e in validate_arrangement(self.items, self.b, pl)))

    def test_detects_overweight(self):
        pl = [self.P(1, "a", 0, 0, 0, wt=6), self.P(2, "b", 5, 0, 0, wt=6)]
        self.assertTrue(any("weight" in e for e in validate_arrangement(self.items, self.b, pl)))

    def test_detects_missing_item(self):
        pl = [self.P(1, "a", 0, 0, 0)]
        self.assertTrue(validate_arrangement(self.items, self.b, pl))

    def test_touching_faces_is_not_overlap(self):
        pl = [self.P(1, "a", 0, 0, 0), self.P(2, "b", 5, 5, 5)]
        self.assertEqual(validate_arrangement(self.items, self.b, pl), [])


class RecommendTests(SimpleTestCase):
    def test_lowest_cost_feasible_selected(self):
        boxes = [box(1, 40, 30, 20, cost="70"), box(2, 25, 20, 15, cost="40"),
                 box(3, 60, 40, 40, cost="120")]
        rec = recommend([item("a", 20, 15, 10, 2)], boxes)
        self.assertEqual(rec.status, "recommended")
        self.assertEqual(rec.chosen.box.id, 2)

    def test_cheapest_box_too_small_is_skipped(self):
        boxes = [box(1, 10, 10, 10, cost="5"), box(2, 40, 40, 40, cost="50")]
        rec = recommend([item("a", 20, 20, 20)], boxes)
        self.assertEqual(rec.chosen.box.id, 2)
        self.assertTrue(rec.cheaper_rejections_all_proven)

    def test_equal_cost_tie_break_smaller_volume_then_id(self):
        boxes = [box(5, 30, 30, 30, cost="50"), box(3, 20, 20, 20, cost="50"),
                 box(2, 20, 20, 20, cost="50")]
        rec = recommend([item("a", 5, 5, 5)], boxes)
        self.assertEqual(rec.chosen.box.id, 2)

    def test_no_suitable_box(self):
        rec = recommend([item("a", 100, 100, 100)], [box(1, 10, 10, 10)])
        self.assertEqual(rec.status, "no_suitable_box")
        self.assertIsNone(rec.chosen)

    def test_no_boxes_configured(self):
        self.assertEqual(recommend([item("a", 1, 1, 1)], []).status, "no_suitable_box")

    def test_two_items_force_bigger_box(self):
        items = [item("c", 6, 6, 6, pid=1)] * 2
        boxes = [box(1, 10, 10, 10, cost="10"), box(2, 12, 12, 12, cost="25")]
        rec = recommend(items, boxes)
        self.assertEqual(rec.chosen.box.id, 2)
        self.assertFalse(rec.cheaper_rejections_all_proven)  # heuristic rejection, honestly flagged

    def test_undetermined_when_limit_hit(self):
        items = [item("c", 6, 6, 6, pid=1)] * 2
        rec = recommend(items, [box(1, 10, 10, 10)], max_nodes=3)
        self.assertEqual(rec.status, "undetermined")

    def test_alternative_feasible_boxes_all_evaluated(self):
        boxes = [box(1, 30, 30, 30, cost="10"), box(2, 40, 40, 40, cost="20")]
        rec = recommend([item("a", 5, 5, 5)], boxes)
        feasible = [e for e in rec.evaluations if e.result.status == PackStatus.FEASIBLE]
        self.assertEqual(len(feasible), 2)
