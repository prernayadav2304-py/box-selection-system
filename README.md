# AI-Assisted Box Selection System

Django 5 + Django REST Framework backend (SQLite) with a small dashboard. Given an order (products + quantities) it recommends the **lowest-cost shipping box in which the items can actually be placed** (3D, with rotation, no overlap, within weight capacity).

Units: dimensions **cm**, weight **kg**, cost **INR (₹)**. Python 3.12, Django 5.2.

## Quick start

macOS / Linux
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo        # optional: DEMO-labelled sample products/boxes
python manage.py runserver
```
Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1      # if blocked: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
Open http://127.0.0.1:8000/ (dashboard). Admin: `python manage.py createsuperuser`, then `/admin/`.

Tests: `python manage.py test -v 2` (60 tests, no extra setup).

## Project layout
```
config/                 settings, urls, wsgi
boxes/packing.py        PURE-PYTHON packing engine (no Django imports)
boxes/services.py       glue: DB models -> packing engine -> JSON response, saves Order
boxes/models.py         Product, ShippingBox, Order, OrderItem (+ DB check constraints)
boxes/serializers.py    input validation
boxes/views.py, urls.py REST API
boxes/templates/dashboard.html   dashboard (vanilla JS, calls the real API)
boxes/test_packing.py   engine unit tests      boxes/test_api.py   API/model tests
```

## API
| Method | URL | Purpose |
|---|---|---|
| GET/POST | `/api/products/` | list (paginated) / create. Fields: name, sku (unique), length, width, height, weight |
| GET/PUT/PATCH/DELETE | `/api/products/<id>/` | delete returns 409 if the product is in an order |
| GET/POST | `/api/boxes/` | name, code (unique), inner_length/width/height, max_weight, cost |
| GET/PUT/PATCH/DELETE | `/api/boxes/<id>/` | |
| POST | `/api/recommend/` | recommend a box; saves an Order |
| GET | `/api/orders/`, `/api/orders/<id>/` | history incl. full stored result |
| GET | `/api/health/` | health check |

Pagination: `?page=2&page_size=50` (max 100).

### Recommend example
```bash
curl -X POST http://127.0.0.1:8000/api/recommend/ -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":1,"quantity":1},{"product_id":2,"quantity":2}]}'
```
Response (abridged): `status` (`recommended` | `no_suitable_box` | `undetermined`), `box` (dimensions, cost, weight/space utilisation, remaining capacity), `placements` (x,y,z and rotated size of every unit), `validation` (independent re-check), `other_suitable_boxes`, `boxes_evaluated` (status + reason for **every** box, cheapest first), `message`, `search_limits`.

Errors: `400` validation (empty order, zero/negative quantity, duplicate `product_id`, unknown product, > 40 units), `409` deleting a used product.

## Algorithm (`boxes/packing.py`)
1. Expand quantities into individual units.
2. **Necessary checks** per box: total weight ≤ capacity; every unit fits in some orientation; total volume ≤ box volume. Failing any = `infeasible_proven` (certain).
3. **Backtracking search**: units sorted largest-volume first; for each unit try each unique orientation (≤ 6 axis-aligned) at candidate positions (grid of 0 and the far faces of already-placed units on each axis); accept only if inside the box and not overlapping; otherwise backtrack. Identical units are forced into a canonical position order to avoid duplicate work.
4. A found arrangement is **re-validated independently** (`validate_arrangement`: non-negative coordinates, inside box, no pairwise overlap, weight) before it is reported as feasible.
5. Boxes are evaluated in order **(cost, volume, id)** — deterministic tie-break — and the first feasible one is recommended.
6. All arithmetic uses `Decimal` (no float errors); touching faces are not overlap.

Statuses: `feasible`, `infeasible_proven`, `infeasible_search_exhausted`, `unknown_limit_reached`.

### Limitations (please read)
- 3D bin packing is NP-hard. Search is bounded by `PACKING_MAX_NODES` (default 50000), `PACKING_MAX_SECONDS` (default 3) and 40 units per order.
- `infeasible_search_exhausted` means the search finished its candidate positions without success. It is **not a mathematical proof**: an unusual arrangement outside the candidate grid / item order could exist. The API flags this via `cheaper_rejections_all_proven: false`.
- If the limit is hit the result is `unknown_limit_reached` — never reported as feasible or infeasible.
- So "cheapest feasible box" is exact only when every cheaper box was rejected by a proven check; otherwise it is "cheapest box for which a valid arrangement was found".
- Not modelled: padding, fragile items, non-box shapes, orientation restrictions ("this side up"), box/packaging weight, gravity/support.
- No authentication (assignment scope); do not expose publicly as-is.

## Configuration
Environment variables (see `.env.example`): `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (1/0), `DJANGO_ALLOWED_HOSTS`, `PACKING_MAX_NODES`, `PACKING_MAX_SECONDS`. With `DJANGO_DEBUG=0` a secret key is required. Dev default key is for local use only.

## Troubleshooting
- `no such table`: run `python manage.py migrate`.
- Dashboard empty: add data in the dashboard or run `python manage.py seed_demo`.
- PowerShell activation blocked: see Windows commands above.

## Submission documents
`AI_USAGE.md`, `TEST_OUTPUT.md`, `LEARNING_REFLECTION.md` (to be written by the candidate), `chat_transcript/` (candidate exports their own chat).
