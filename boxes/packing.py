"""
3D box-packing engine. Pure Python: no Django imports, so it is unit-testable alone.

Units: dimensions in centimetres, weights in kilograms, cost in INR.
All arithmetic uses ``decimal.Decimal`` (no float comparison errors).

Algorithm (see README for the long version)
-------------------------------------------
For one box, ``pack()`` runs a depth-first backtracking search:
  * items are sorted largest-volume first (deterministic order);
  * for each item every unique axis-aligned orientation (up to 6) is tried;
  * candidate positions are the "grid" of coordinates formed by 0 and the far
    faces of items already placed, on each axis;
  * a placement is accepted only if it is inside the box and overlaps nobody;
  * if a later item cannot be placed we backtrack and try another choice;
  * identical items are forced into a canonical position order (symmetry
    breaking) so we do not explore the same arrangement many times.

Statuses (never over-claim):
  FEASIBLE                  valid arrangement found AND independently validated.
  INFEASIBLE_PROVEN         a necessary condition fails (weight, total volume, or
                            an item that fits in no orientation). Mathematically certain.
  INFEASIBLE_SEARCH_EXHAUSTED  the whole candidate-position search finished with
                            no solution. NOT a proof: the search only tries
                            positions from the candidate grid and a fixed item
                            order, so an exotic arrangement could be missed.
  UNKNOWN_LIMIT_REACHED     node or time limit hit; nothing can be claimed.

Complexity: worst case exponential in the number of items (3D bin packing is
NP-hard). ``max_nodes`` / ``max_seconds`` bound the work.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from itertools import permutations
from typing import Optional, Sequence

ZERO = Decimal("0")


class PackStatus(str, Enum):
    FEASIBLE = "feasible"
    INFEASIBLE_PROVEN = "infeasible_proven"
    INFEASIBLE_SEARCH_EXHAUSTED = "infeasible_search_exhausted"
    UNKNOWN_LIMIT_REACHED = "unknown_limit_reached"


@dataclass(frozen=True)
class Item:
    """One physical unit to pack (a product with quantity 3 -> 3 Items)."""
    product_id: int
    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    weight: Decimal

    @property
    def volume(self) -> Decimal:
        return self.length * self.width * self.height

    def orientations(self) -> list[tuple[Decimal, Decimal, Decimal]]:
        return sorted(set(permutations((self.length, self.width, self.height))))


@dataclass(frozen=True)
class BoxSpec:
    id: int
    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    max_weight: Decimal
    cost: Decimal

    @property
    def volume(self) -> Decimal:
        return self.length * self.width * self.height


@dataclass(frozen=True)
class Placement:
    product_id: int
    name: str
    x: Decimal
    y: Decimal
    z: Decimal
    length: Decimal  # placed (rotated) size along x
    width: Decimal   # along y
    height: Decimal  # along z
    weight: Decimal


@dataclass
class PackResult:
    status: PackStatus
    reason: str
    placements: list[Placement] = field(default_factory=list)
    nodes_explored: int = 0
    validation_errors: list[str] = field(default_factory=list)


def _overlap(a: Placement, b: Placement) -> bool:
    """True if the two cuboids share positive volume (touching faces is fine)."""
    return (
        a.x < b.x + b.length and b.x < a.x + a.length
        and a.y < b.y + b.width and b.y < a.y + a.width
        and a.z < b.z + b.height and b.z < a.z + a.height
    )


def validate_arrangement(items: Sequence[Item], box: BoxSpec,
                         placements: Sequence[Placement]) -> list[str]:
    """Independent checker. Returns a list of problems (empty list == valid)."""
    errors: list[str] = []
    if len(placements) != len(items):
        errors.append(f"expected {len(items)} placements, got {len(placements)}")

    # every item must be matched by a placement that is a rotation of it
    remaining = list(items)
    for p in placements:
        match = None
        for it in remaining:
            if (it.product_id == p.product_id
                    and sorted((it.length, it.width, it.height)) == sorted((p.length, p.width, p.height))):
                match = it
                break
        if match is None:
            errors.append(f"placement of {p.name} does not correspond to an unplaced item/rotation")
        else:
            remaining.remove(match)

    for p in placements:
        if p.x < 0 or p.y < 0 or p.z < 0:
            errors.append(f"{p.name}: negative coordinate")
        if p.x + p.length > box.length or p.y + p.width > box.width or p.z + p.height > box.height:
            errors.append(f"{p.name}: outside box boundaries")
    for i, a in enumerate(placements):
        for b in placements[i + 1:]:
            if _overlap(a, b):
                errors.append(f"{a.name} overlaps {b.name}")

    total = sum((p.weight for p in placements), ZERO)
    if total > box.max_weight:
        errors.append(f"total weight {total} exceeds capacity {box.max_weight}")
    return errors


def pack(items: Sequence[Item], box: BoxSpec, max_nodes: int = 50000,
         max_seconds: float = 3.0) -> PackResult:
    """Try to pack ``items`` into ``box``. See module docstring for statuses."""
    items = list(items)
    if not items:
        return PackResult(PackStatus.INFEASIBLE_PROVEN, "Order has no items.")

    # ---- necessary conditions (these give *proven* infeasibility) ----
    total_weight = sum((i.weight for i in items), ZERO)
    if total_weight > box.max_weight:
        return PackResult(PackStatus.INFEASIBLE_PROVEN,
                          f"Total weight {total_weight} kg exceeds box capacity {box.max_weight} kg.")
    for it in items:
        if not any(l <= box.length and w <= box.width and h <= box.height
                   for l, w, h in it.orientations()):
            return PackResult(PackStatus.INFEASIBLE_PROVEN,
                              f"'{it.name}' ({it.length}x{it.width}x{it.height} cm) does not fit "
                              f"the box interior in any orientation.")
    total_volume = sum((i.volume for i in items), ZERO)
    if total_volume > box.volume:
        return PackResult(PackStatus.INFEASIBLE_PROVEN,
                          f"Total item volume {total_volume} cm3 exceeds box volume {box.volume} cm3.")

    # ---- backtracking search ----
    order = sorted(range(len(items)),
                   key=lambda i: (-items[i].volume, -items[i].weight, items[i].product_id, i))
    ordered = [items[i] for i in order]
    # group id for identical-dimension items (symmetry breaking)
    group_key = [(it.product_id, tuple(sorted((it.length, it.width, it.height)))) for it in ordered]

    placed: list[Placement] = []
    last_pos: list[Optional[tuple]] = [None] * len(ordered)
    state = {"nodes": 0, "limit": False}
    deadline = time.monotonic() + max_seconds

    def candidate_points() -> list[tuple[Decimal, Decimal, Decimal]]:
        xs, ys, zs = {ZERO}, {ZERO}, {ZERO}
        for p in placed:
            xs.add(p.x + p.length)
            ys.add(p.y + p.width)
            zs.add(p.z + p.height)
        pts = [(x, y, z) for z in zs for y in ys for x in xs]
        pts.sort(key=lambda t: (t[2], t[1], t[0]))  # bottom-first, deterministic
        return pts

    def search(k: int) -> bool:
        if k == len(ordered):
            return True
        item = ordered[k]
        same_as_prev = k > 0 and group_key[k] == group_key[k - 1]
        min_pos = last_pos[k - 1] if same_as_prev else None
        for (l, w, h) in item.orientations():
            for (x, y, z) in candidate_points():
                state["nodes"] += 1
                if state["nodes"] > max_nodes or (state["nodes"] % 256 == 0 and time.monotonic() > deadline):
                    state["limit"] = True
                    return False
                if x + l > box.length or y + w > box.width or z + h > box.height:
                    continue
                pos_key = (z, y, x)
                if min_pos is not None and pos_key <= min_pos:
                    continue
                cand = Placement(item.product_id, item.name, x, y, z, l, w, h, item.weight)
                if any(_overlap(cand, p) for p in placed):
                    continue
                placed.append(cand)
                last_pos[k] = pos_key
                if search(k + 1):
                    return True
                placed.pop()
                last_pos[k] = None
                if state["limit"]:
                    return False
        return False

    found = search(0)
    nodes = state["nodes"]
    if found:
        errors = validate_arrangement(items, box, placed)
        if errors:  # should never happen; refuse to claim feasibility
            return PackResult(PackStatus.UNKNOWN_LIMIT_REACHED,
                              "Internal validation failed; arrangement discarded.",
                              [], nodes, errors)
        return PackResult(PackStatus.FEASIBLE, "Valid non-overlapping arrangement found.",
                          list(placed), nodes, [])
    if state["limit"]:
        return PackResult(PackStatus.UNKNOWN_LIMIT_REACHED,
                          f"Search limit reached ({max_nodes} nodes / {max_seconds}s); "
                          f"cannot say whether the items fit.", [], nodes)
    return PackResult(PackStatus.INFEASIBLE_SEARCH_EXHAUSTED,
                      "Items individually fit but no arrangement was found after searching all "
                      "candidate positions (heuristic scope, not a mathematical proof).", [], nodes)


# --------------------------------------------------------------------------
# Box recommendation
# --------------------------------------------------------------------------
@dataclass
class BoxEvaluation:
    box: BoxSpec
    result: PackResult


@dataclass
class Recommendation:
    status: str  # "recommended" | "no_suitable_box" | "undetermined"
    chosen: Optional[BoxEvaluation]
    evaluations: list[BoxEvaluation]
    total_weight: Decimal
    total_volume: Decimal
    cheaper_rejections_all_proven: bool
    message: str


def box_sort_key(box: BoxSpec):
    """Deterministic tie-break: cost, then smaller volume, then lower id."""
    return (box.cost, box.volume, box.id)


def recommend(items: Sequence[Item], boxes: Sequence[BoxSpec], max_nodes: int = 50000,
              max_seconds: float = 3.0) -> Recommendation:
    items = list(items)
    total_weight = sum((i.weight for i in items), ZERO)
    total_volume = sum((i.volume for i in items), ZERO)
    evaluations = [BoxEvaluation(b, pack(items, b, max_nodes, max_seconds))
                   for b in sorted(boxes, key=box_sort_key)]

    chosen = next((e for e in evaluations if e.result.status == PackStatus.FEASIBLE), None)
    if chosen is not None:
        cheaper = evaluations[:evaluations.index(chosen)]
        all_proven = all(e.result.status == PackStatus.INFEASIBLE_PROVEN for e in cheaper)
        if any(e.result.status == PackStatus.UNKNOWN_LIMIT_REACHED for e in cheaper):
            msg = ("A box was found, but a cheaper box could not be evaluated within the search "
                   "limit, so this may not be the cheapest feasible box.")
        elif not all_proven:
            msg = ("Cheapest box for which a valid arrangement was found. Cheaper boxes were "
                   "rejected by heuristic search, not by proof.")
        else:
            msg = "Cheapest box that can hold the order; all cheaper boxes were rejected with certainty."
        return Recommendation("recommended", chosen, evaluations, total_weight, total_volume,
                              all_proven, msg)

    if any(e.result.status == PackStatus.UNKNOWN_LIMIT_REACHED for e in evaluations):
        return Recommendation("undetermined", None, evaluations, total_weight, total_volume, False,
                              "No box confirmed; at least one box hit the search limit.")
    return Recommendation("no_suitable_box", None, evaluations, total_weight, total_volume,
                          all(e.result.status == PackStatus.INFEASIBLE_PROVEN for e in evaluations),
                          "No suitable box found for this order.")
