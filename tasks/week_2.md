# Week 2 — Multi-Store + Real Optimizer

## Goals
- Add Tesco (UK) and BigBasket (IN) scrapers with tests and freshness scheduling.
- Implement PuLP optimizer with budget/nutrition/variety constraints and per-item caps.
- Expose real price API and assemble meal plans with normalized units and data provenance.

## Tasks
- Scrapers: Tesco + BigBasket using selector-first approach; expand golden pages and tests; store snapshots.
- Scheduling: QStash scheduled jobs per store SLA (SPAR weekly, Tesco/BigBasket 2x/week, Walmart daily placeholder).
- Price API: `/api/prices?city=&category=` with freshness filter and `last_updated`, `source_type` fields.
- Optimizer: PuLP LP solver with constraints—budget ±2%, protein target, per-category max, per-item max units, minimum meal variety; return feasibility codes.
- Reporter: build meals + shopping list with normalized units, price_per_unit, store links, and data source; handle infeasible cases gracefully.
- Frontend: render real prices, show stale badge when beyond SLA, add loading/error states.
- Ops: rate-limit `/api/scrape/trigger`, env templates, alerts on scrape failure >10% or SLA breach.

## Checkpoints
- Scraper tests pass for SPAR, Tesco, BigBasket; snapshots updated when selectors change.
- Scheduled jobs visible in QStash dashboard; manual trigger logs show store/city/pricing_version.
- Optimizer unit tests pass on synthetic tables (feasible/infeasible/budget edge cases).
- `/api/prices` returns filtered, fresh results with timestamps and source type.
- Meal-plan responses include normalized quantities and clear infeasibility messages when applicable.
- Frontend shows stale indicator when data exceeds SLA.

## Verification
- `pytest` in `backend/` covers scrapers, normalization, optimizer.
- Manual curl: `/api/prices?city=vienna&category=protein` returns fresh rows with `last_updated`.
- Meal-plan request returns within budget and meets protein/variety constraints in tests.
- Logs/alerts show no scrape failure spikes; rate limiting confirmed on `/api/scrape/trigger`.
