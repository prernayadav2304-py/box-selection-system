# AI Usage

> DRAFT written from the visible chat history. **Candidate: read every line, correct anything that is not true for you, and fill the [# AI Usage

## 1. AI Tools Used
- **ChatGPT:** Used to understand the assignment requirements, generate initial project code, and identify missing features.
- **Claude:** Used for additional project development and code review, if applicable.
- Other tools: [Add any other tools actually used.]

## 2. Prompts Given
I asked AI tools to explain the assignment, provide a complete project structure and runnable code, check whether the project met all requirements, implement the multi-product packing algorithm, improve the dashboard UI, and prepare a final project ZIP.

## 3. Output Accepted
I used AI-generated code and suggestions for the Django and Django REST Framework backend, packing logic, validation, tests, and dashboard. I reviewed the final implementation to the extent I could understand and verify it.

## 4. Output Rejected or Modified
I requested improvements when the initial versions did not cover all assignment requirements. The packing algorithm, product identification, validation, and dashboard were revised to better meet the requirements. I retained only changes that were appropriate for the assignment.

## 5. Mistakes and Limitations
The initial project versions had incomplete functionality and potential code and testing issues. This showed me why generated code must be checked rather than assumed to be complete. I also learned that passing tests alone does not guarantee that every feature works correctly.

## 6. Verification
The final draft reports automated tests and a server smoke test. I will confirm the actual commands, test results, and features I personally verified before submitting. Browser testing, Windows compatibility, and CI execution should be reported as unverified unless I test them myself.] parts yourself.** Only keep statements that are accurate.

## 1. AI tools used
- ChatGPT (earlier chat: explained the assignment, produced starter ZIPs v1 and v2).
- Claude (this final project: rewrote the packing engine, API, tests, dashboard and docs, and ran the tests).
- [FILL IN: any other tool, or correct the above]

## 2. Prompts given (my words, as sent)
- "short me project smjha do actual krna kya h or kese"
- "plzz pura project complete structure/ file folder with their complete code ready to run code dedo in zip.file"
- "kya ye pura complete zip h complete mtlb sbhi logic assignment ke , UI bhi perfect h kya ??"
- "Multi-product packing algorithm / UI / frontend dashboard — ye dono point bhi complete krdo"
- A long "production-quality full-stack" prompt (React, Three.js, Docker, JWT, etc.) was pasted; the AI advised trimming it (see 4).
- "create a complete zip of project , ready to send to hiring team"
- [FILL IN: other prompts you sent that are not visible here]

## 3. Output accepted
- Django + DRF + SQLite structure with the packing logic isolated in `boxes/packing.py`.
- Backtracking search with 6 rotations, candidate positions, Decimal arithmetic, deterministic tie-break (cost, volume, id), and four honest statuses (`feasible`, `infeasible_proven`, `infeasible_search_exhausted`, `unknown_limit_reached`).
- Independent `validate_arrangement` check; order persistence; dashboard using the real API.
- [FILL IN: what you reviewed and understood well enough to explain]

## 4. Output rejected or modified
- The huge full-stack prompt (React/Vite/Three.js/Docker/auth/Swagger) was **not** used: assignment is Django-based, scope was trimmed to what I can explain and verify. [FILL IN: your own reasoning in your words]
- v2 ZIP's greedy single-pass packing was replaced by backtracking search with a validator.
- v2 `Product.name`-only identity replaced by unique `sku`; box has unique `code`; product input uses quantities.
- [FILL IN: anything you changed yourself]

## 5. Mistakes made by the AI
- v1/v2 ZIPs were never run (only a syntax check) yet were presented as "complete"; the AI later admitted they were not complete.
- v2 `settings.py` used a non-existent context processor `django.contrib.messages.context_processors.static` (should be `messages`) — would crash on run.
- v2 `boxes/tests.py` first contained invalid Python (`from .services import product_fits_box if False else recommend_box`) before being overwritten.
- v2 tests were missing several required cases (zero/negative/missing dimensions, tie-break, items that fit individually but not together).
- v2 README wording suggested the 3D result was more reliable than a heuristic can guarantee.
- [FILL IN: bugs you found yourself while running/reviewing]

## 6. How the final code was verified
- Clean virtualenv from `requirements.txt`; `python manage.py check`, `makemigrations --check`, `python manage.py test -v 2` → 60 tests OK (full output in `TEST_OUTPUT.md`).
- Live server smoke test with curl on a clean database, plus restart to confirm persistence.
- Tests include: rotation, exact fit, overweight, items fit individually but not together, overlap/out-of-bounds/negative-coordinate detection, search-limit → unknown, tie-break, empty order, duplicate IDs, zero/negative input, random arrangements re-validated.
- [FILL IN: what you ran yourself on your machine, and the result]
- Not verified by the AI: the dashboard in a real browser, Windows, GitHub Actions run.
