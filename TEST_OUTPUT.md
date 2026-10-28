# Test Output

All output below was produced by actually running the commands (not edited). It was run in the AI assistant's Linux sandbox in a **fresh virtualenv** created from `requirements.txt`.

> **Candidate: re-run `python manage.py test -v 2` on your own machine and append your own output below (and/or add your GitHub Actions link).** Your output is the one that proves it works for you.

## 1. Automated tests (sandbox, fresh venv)
```
$ python --version
Python 3.12.3

$ pip freeze (relevant)
asgiref==3.13.0
Django==5.2.18
djangorestframework==3.18.3
sqlparse==0.6.0

$ python manage.py makemigrations --check --dry-run
No changes detected

$ python manage.py check
System check identified no issues (0 silenced).

$ python manage.py test -v 2
Found 60 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, boxes, contenttypes, sessions
System check identified no issues (0 silenced).
test_create (boxes.test_api.BoxAPITests.test_create) ... ok
test_duplicate_code_rejected (boxes.test_api.BoxAPITests.test_duplicate_code_rejected) ... ok
test_invalid_values_rejected (boxes.test_api.BoxAPITests.test_invalid_values_rejected) ... ok
test_cannot_delete_product_used_in_order (boxes.test_api.ProductAPITests.test_cannot_delete_product_used_in_order) ... ok
test_create_and_list (boxes.test_api.ProductAPITests.test_create_and_list) ... ok
test_db_constraint_blocks_zero (boxes.test_api.ProductAPITests.test_db_constraint_blocks_zero) ... ok
test_duplicate_sku_rejected (boxes.test_api.ProductAPITests.test_duplicate_sku_rejected) ... ok
test_missing_dimension_rejected (boxes.test_api.ProductAPITests.test_missing_dimension_rejected) ... ok
test_negative_dimension_rejected (boxes.test_api.ProductAPITests.test_negative_dimension_rejected) ... ok
test_negative_weight_rejected (boxes.test_api.ProductAPITests.test_negative_weight_rejected) ... ok
test_non_numeric_rejected (boxes.test_api.ProductAPITests.test_non_numeric_rejected) ... ok
test_update_and_delete (boxes.test_api.ProductAPITests.test_update_and_delete) ... ok
test_zero_dimension_rejected (boxes.test_api.ProductAPITests.test_zero_dimension_rejected) ... ok
test_duplicate_product_ids_rejected (boxes.test_api.RecommendAPITests.test_duplicate_product_ids_rejected) ... ok
test_empty_order_rejected (boxes.test_api.RecommendAPITests.test_empty_order_rejected) ... ok
test_health_and_dashboard (boxes.test_api.RecommendAPITests.test_health_and_dashboard) ... ok
test_individually_fit_but_not_together_goes_to_bigger_box (boxes.test_api.RecommendAPITests.test_individually_fit_but_not_together_goes_to_bigger_box) ... ok
test_invalid_request_does_not_create_order (boxes.test_api.RecommendAPITests.test_invalid_request_does_not_create_order) ... ok
test_missing_items_key_rejected (boxes.test_api.RecommendAPITests.test_missing_items_key_rejected) ... ok
test_multiple_products (boxes.test_api.RecommendAPITests.test_multiple_products) ... ok
test_no_suitable_box (boxes.test_api.RecommendAPITests.test_no_suitable_box) ... ok
test_order_persisted_and_listed (boxes.test_api.RecommendAPITests.test_order_persisted_and_listed) ... ok
test_quantity_counts_weight_and_placements (boxes.test_api.RecommendAPITests.test_quantity_counts_weight_and_placements) ... ok
test_quantity_pushes_to_bigger_box_by_weight (boxes.test_api.RecommendAPITests.test_quantity_pushes_to_bigger_box_by_weight) ... ok
test_returned_placements_are_inside_box (boxes.test_api.RecommendAPITests.test_returned_placements_are_inside_box) ... ok
test_single_product_cheapest_box (boxes.test_api.RecommendAPITests.test_single_product_cheapest_box) ... ok
test_too_many_units_rejected (boxes.test_api.RecommendAPITests.test_too_many_units_rejected) ... ok
test_unknown_product_rejected (boxes.test_api.RecommendAPITests.test_unknown_product_rejected) ... ok
test_zero_and_negative_quantity_rejected (boxes.test_api.RecommendAPITests.test_zero_and_negative_quantity_rejected) ... ok
test_eight_cubes_exact_fill (boxes.test_packing.MultiItemPackingTests.test_eight_cubes_exact_fill) ... ok
test_individually_fit_but_not_together (boxes.test_packing.MultiItemPackingTests.test_individually_fit_but_not_together) ... ok
test_needs_backtracking_arrangement (boxes.test_packing.MultiItemPackingTests.test_needs_backtracking_arrangement) ... ok
test_random_feasible_results_always_validate (boxes.test_packing.MultiItemPackingTests.test_random_feasible_results_always_validate) ... ok
test_search_limit_reports_unknown_not_feasible (boxes.test_packing.MultiItemPackingTests.test_search_limit_reports_unknown_not_feasible) ... ok
test_total_volume_too_large_proven (boxes.test_packing.MultiItemPackingTests.test_total_volume_too_large_proven) ... ok
test_two_items_side_by_side (boxes.test_packing.MultiItemPackingTests.test_two_items_side_by_side) ... ok
test_alternative_feasible_boxes_all_evaluated (boxes.test_packing.RecommendTests.test_alternative_feasible_boxes_all_evaluated) ... ok
test_cheapest_box_too_small_is_skipped (boxes.test_packing.RecommendTests.test_cheapest_box_too_small_is_skipped) ... ok
test_equal_cost_tie_break_smaller_volume_then_id (boxes.test_packing.RecommendTests.test_equal_cost_tie_break_smaller_volume_then_id) ... ok
test_lowest_cost_feasible_selected (boxes.test_packing.RecommendTests.test_lowest_cost_feasible_selected) ... ok
test_no_boxes_configured (boxes.test_packing.RecommendTests.test_no_boxes_configured) ... ok
test_no_suitable_box (boxes.test_packing.RecommendTests.test_no_suitable_box) ... ok
test_two_items_force_bigger_box (boxes.test_packing.RecommendTests.test_two_items_force_bigger_box) ... ok
test_undetermined_when_limit_hit (boxes.test_packing.RecommendTests.test_undetermined_when_limit_hit) ... ok
test_decimal_precision_no_float_error (boxes.test_packing.SinglePackingTests.test_decimal_precision_no_float_error) ... ok
test_empty_items_not_feasible (boxes.test_packing.SinglePackingTests.test_empty_items_not_feasible) ... ok
test_exact_boundary_fit (boxes.test_packing.SinglePackingTests.test_exact_boundary_fit) ... ok
test_item_larger_than_box_rejected (boxes.test_packing.SinglePackingTests.test_item_larger_than_box_rejected) ... ok
test_one_millimetre_too_big_rejected_with_proof (boxes.test_packing.SinglePackingTests.test_one_millimetre_too_big_rejected_with_proof) ... ok
test_rotation_needed (boxes.test_packing.SinglePackingTests.test_rotation_needed) ... ok
test_single_item_fits (boxes.test_packing.SinglePackingTests.test_single_item_fits) ... ok
test_weight_exactly_at_capacity_is_allowed (boxes.test_packing.SinglePackingTests.test_weight_exactly_at_capacity_is_allowed) ... ok
test_weight_exceeded_rejected (boxes.test_packing.SinglePackingTests.test_weight_exceeded_rejected) ... ok
test_detects_missing_item (boxes.test_packing.ValidatorTests.test_detects_missing_item) ... ok
test_detects_negative_coordinate (boxes.test_packing.ValidatorTests.test_detects_negative_coordinate) ... ok
test_detects_outside_box (boxes.test_packing.ValidatorTests.test_detects_outside_box) ... ok
test_detects_overlap (boxes.test_packing.ValidatorTests.test_detects_overlap) ... ok
test_detects_overweight (boxes.test_packing.ValidatorTests.test_detects_overweight) ... ok
test_touching_faces_is_not_overlap (boxes.test_packing.ValidatorTests.test_touching_faces_is_not_overlap) ... ok
test_valid (boxes.test_packing.ValidatorTests.test_valid) ... ok

----------------------------------------------------------------------
Ran 60 tests in 0.120s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

## 2. Manual smoke test (sandbox, live `runserver`, clean DB)
Commands: `migrate`, `seed_demo`, `runserver`, then curl.
```
GET  /api/health/                      -> {"status":"ok"}
GET  /                                 -> HTTP 200 (dashboard)
POST /api/recommend/ book x1 + mug x2  -> recommended, Demo Small Box, cost 40.00, validation valid=True, 3 placements
     message: "Cheapest box that can hold the order; all cheaper boxes were rejected with certainty."
POST /api/recommend/ {"items":[]}      -> 400 {"items":{"non_field_errors":["This list may not be empty."]}}
POST /api/products/ length="0"         -> 400 {"length":["Ensure this value is greater than or equal to 0.01."]}
Restart server, GET /api/orders/       -> count 1 (order persisted across restart)
```

## 3. Packing benchmark (sandbox, limits 50000 nodes / 3 s)
```
27 cubes 5cm in 15x15x15 (exact fill):  feasible                     nodes=594
40 cubes 4cm in 30x30x30:               feasible                     nodes=915
12 mixed items in 30x20x15:             feasible                     nodes=112
2 cubes 6cm in 10x10x10:                infeasible_search_exhausted  nodes=9
3 cubes 6cm in 11x11x11:                infeasible_search_exhausted  nodes=9
```

## Not verified
- Not run on Windows / on the candidate's machine.
- GitHub Actions workflow (`.github/workflows/tests.yml`) written but not yet executed — it runs after you push.
- Browser UI was not clicked through in a real browser here; only HTTP 200 for the page and the API calls above were checked. Please click through the dashboard once (add product, add box, find best box, delete) before submitting.
- No load/performance testing beyond the benchmark above.

## 4. My machine (Windows)

PS C:\Users\admin\Downloads\box_selection_system\box_selection_system> py -m venv .venv
>> .\.venv\Scripts\Activate.ps1
>> python -m pip install -r requirements.txt
>> python manage.py test -v 2
Collecting Django==5.2.18 (from -r requirements.txt (line 1))
  Downloading django-5.2.18-py3-none-any.whl.metadata (4.1 kB)
Collecting djangorestframework==3.18.3 (from -r requirements.txt (line 2))
  Downloading djangorestframework-3.18.3-py3-none-any.whl.metadata (7.8 kB)
Collecting asgiref>=3.8.1 (from Django==5.2.18->-r requirements.txt (line 1))
  Downloading asgiref-3.13.0-py3-none-any.whl.metadata (12 kB)
Collecting sqlparse>=0.3.1 (from Django==5.2.18->-r requirements.txt (line 1))
  Downloading sqlparse-0.6.0-py3-none-any.whl.metadata (6.0 kB)
Collecting tzdata (from Django==5.2.18->-r requirements.txt (line 1))
  Downloading tzdata-2026.5-py2.py3-none-any.whl.metadata (1.4 kB)
Downloading django-5.2.18-py3-none-any.whl (8.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.3/8.3 MB 5.4 MB/s  0:00:01
Downloading djangorestframework-3.18.3-py3-none-any.whl (903 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 904.0/904.0 kB 7.1 MB/s  0:00:00
Downloading asgiref-3.13.0-py3-none-any.whl (27 kB)
Downloading sqlparse-0.6.0-py3-none-any.whl (50 kB)
Downloading tzdata-2026.5-py2.py3-none-any.whl (347 kB)
Installing collected packages: tzdata, sqlparse, asgiref, Django, djangorestframework
Successfully installed Django-5.2.18 asgiref-3.13.0 djangorestframework-3.18.3 sqlparse-0.6.0 tzdata-2026.5

[notice] A new release of pip is available: 25.3 -> 26.2.2
[notice] To update, run: python.exe -m pip install --upgrade pip
Found 60 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, boxes, contenttypes, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying boxes.0001_initial... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
test_create (boxes.test_api.BoxAPITests.test_create) ... ok
test_duplicate_code_rejected (boxes.test_api.BoxAPITests.test_duplicate_code_rejected) ... ok
test_invalid_values_rejected (boxes.test_api.BoxAPITests.test_invalid_values_rejected) ... ok
test_cannot_delete_product_used_in_order (boxes.test_api.ProductAPITests.test_cannot_delete_product_used_in_order) ... ok
test_create_and_list (boxes.test_api.ProductAPITests.test_create_and_list) ... ok
test_db_constraint_blocks_zero (boxes.test_api.ProductAPITests.test_db_constraint_blocks_zero) ... ok
test_duplicate_sku_rejected (boxes.test_api.ProductAPITests.test_duplicate_sku_rejected) ... ok
test_missing_dimension_rejected (boxes.test_api.ProductAPITests.test_missing_dimension_rejected) ... ok
test_negative_dimension_rejected (boxes.test_api.ProductAPITests.test_negative_dimension_rejected) ... ok
test_negative_weight_rejected (boxes.test_api.ProductAPITests.test_negative_weight_rejected) ... ok
test_non_numeric_rejected (boxes.test_api.ProductAPITests.test_non_numeric_rejected) ... ok
test_update_and_delete (boxes.test_api.ProductAPITests.test_update_and_delete) ... ok
test_zero_dimension_rejected (boxes.test_api.ProductAPITests.test_zero_dimension_rejected) ... ok
test_duplicate_product_ids_rejected (boxes.test_api.RecommendAPITests.test_duplicate_product_ids_rejected) ... ok
test_empty_order_rejected (boxes.test_api.RecommendAPITests.test_empty_order_rejected) ... ok
test_health_and_dashboard (boxes.test_api.RecommendAPITests.test_health_and_dashboard) ... ok
test_individually_fit_but_not_together_goes_to_bigger_box (boxes.test_api.RecommendAPITests.test_individually_fit_but_not_together_goes_to_bigger_box) ... ok
test_invalid_request_does_not_create_order (boxes.test_api.RecommendAPITests.test_invalid_request_does_not_create_order) ... ok
test_missing_items_key_rejected (boxes.test_api.RecommendAPITests.test_missing_items_key_rejected) ... ok
test_multiple_products (boxes.test_api.RecommendAPITests.test_multiple_products) ... ok
test_no_suitable_box (boxes.test_api.RecommendAPITests.test_no_suitable_box) ... ok
test_order_persisted_and_listed (boxes.test_api.RecommendAPITests.test_order_persisted_and_listed) ... ok
test_quantity_counts_weight_and_placements (boxes.test_api.RecommendAPITests.test_quantity_counts_weight_and_placements) ... ok
test_quantity_pushes_to_bigger_box_by_weight (boxes.test_api.RecommendAPITests.test_quantity_pushes_to_bigger_box_by_weight) ... ok
test_returned_placements_are_inside_box (boxes.test_api.RecommendAPITests.test_returned_placements_are_inside_box) ... ok
test_single_product_cheapest_box (boxes.test_api.RecommendAPITests.test_single_product_cheapest_box) ... ok
test_too_many_units_rejected (boxes.test_api.RecommendAPITests.test_too_many_units_rejected) ... ok
test_unknown_product_rejected (boxes.test_api.RecommendAPITests.test_unknown_product_rejected) ... ok
test_zero_and_negative_quantity_rejected (boxes.test_api.RecommendAPITests.test_zero_and_negative_quantity_rejected) ... ok
test_eight_cubes_exact_fill (boxes.test_packing.MultiItemPackingTests.test_eight_cubes_exact_fill) ... ok
test_individually_fit_but_not_together (boxes.test_packing.MultiItemPackingTests.test_individually_fit_but_not_together) ... ok
test_needs_backtracking_arrangement (boxes.test_packing.MultiItemPackingTests.test_needs_backtracking_arrangement) ... ok
test_random_feasible_results_always_validate (boxes.test_packing.MultiItemPackingTests.test_random_feasible_results_always_validate) ... ok
test_search_limit_reports_unknown_not_feasible (boxes.test_packing.MultiItemPackingTests.test_search_limit_reports_unknown_not_feasible) ... ok
test_total_volume_too_large_proven (boxes.test_packing.MultiItemPackingTests.test_total_volume_too_large_proven) ... ok
test_two_items_side_by_side (boxes.test_packing.MultiItemPackingTests.test_two_items_side_by_side) ... ok
test_alternative_feasible_boxes_all_evaluated (boxes.test_packing.RecommendTests.test_alternative_feasible_boxes_all_evaluated) ... ok
test_cheapest_box_too_small_is_skipped (boxes.test_packing.RecommendTests.test_cheapest_box_too_small_is_skipped) ... ok
test_equal_cost_tie_break_smaller_volume_then_id (boxes.test_packing.RecommendTests.test_equal_cost_tie_break_smaller_volume_then_id) ... ok
test_lowest_cost_feasible_selected (boxes.test_packing.RecommendTests.test_lowest_cost_feasible_selected) ... ok
test_no_boxes_configured (boxes.test_packing.RecommendTests.test_no_boxes_configured) ... ok
test_no_suitable_box (boxes.test_packing.RecommendTests.test_no_suitable_box) ... ok
test_two_items_force_bigger_box (boxes.test_packing.RecommendTests.test_two_items_force_bigger_box) ... ok
test_undetermined_when_limit_hit (boxes.test_packing.RecommendTests.test_undetermined_when_limit_hit) ... ok
test_decimal_precision_no_float_error (boxes.test_packing.SinglePackingTests.test_decimal_precision_no_float_error) ... ok
test_empty_items_not_feasible (boxes.test_packing.SinglePackingTests.test_empty_items_not_feasible) ... ok
test_exact_boundary_fit (boxes.test_packing.SinglePackingTests.test_exact_boundary_fit) ... ok
test_item_larger_than_box_rejected (boxes.test_packing.SinglePackingTests.test_item_larger_than_box_rejected) ... ok
test_one_millimetre_too_big_rejected_with_proof (boxes.test_packing.SinglePackingTests.test_one_millimetre_too_big_rejected_with_proof) ... ok
test_rotation_needed (boxes.test_packing.SinglePackingTests.test_rotation_needed) ... ok
test_single_item_fits (boxes.test_packing.SinglePackingTests.test_single_item_fits) ... ok
test_weight_exactly_at_capacity_is_allowed (boxes.test_packing.SinglePackingTests.test_weight_exactly_at_capacity_is_allowed) ... ok
test_weight_exceeded_rejected (boxes.test_packing.SinglePackingTests.test_weight_exceeded_rejected) ... ok
test_detects_missing_item (boxes.test_packing.ValidatorTests.test_detects_missing_item) ... ok
test_detects_negative_coordinate (boxes.test_packing.ValidatorTests.test_detects_negative_coordinate) ... ok
test_detects_outside_box (boxes.test_packing.ValidatorTests.test_detects_outside_box) ... ok
test_detects_overlap (boxes.test_packing.ValidatorTests.test_detects_overlap) ... ok
test_detects_overweight (boxes.test_packing.ValidatorTests.test_detects_overweight) ... ok
test_touching_faces_is_not_overlap (boxes.test_packing.ValidatorTests.test_touching_faces_is_not_overlap) ... ok
test_valid (boxes.test_packing.ValidatorTests.test_valid) ... ok

----------------------------------------------------------------------
Ran 60 tests in 0.298s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
(.venv) PS C:\Users\admin\Downloads\box_selection_system\box_selection_system> 