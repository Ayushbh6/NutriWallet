# Week 1 — Price Fetcher POC & Plumbing

## Goals
- FastAPI skeleton with meal-plan and prices endpoints wired to queue stubs.
- Supabase schema deployed (normalization fields) and seed product list.
- SPAR Vienna scraper with selector-first parsing, golden pages, and tests.
- Normalization helpers and structured logging in place.

## Tasks
- Backend scaffold: `/api/meal-plan`, `/api/prices`, health check; Pydantic schemas.
- Queue wiring: QStash client; define messages `scrape_prices`, `plan_meals`; worker stub logs payloads.
- DB: apply schema with normalization fields (package_size/unit, normalized_quantity/unit, source_type, confidence, pricing_version); seed products.
- Scraper: SPAR Vienna selector-based parser; LLM fallback only on selector miss; store HTML/markdown snapshots.
- Tests: golden-page fixtures (~10 items) for SPAR parser; unit tests for normalization helpers (unit parsing, price_per_unit).
- Logging: structured logs with job_id, store, city, pricing_version, source_type; simple failure-rate counter.
- Frontend stub: Next.js page calling `/api/meal-plan` and displaying placeholder prices with `last_updated`.

## Checkpoints
- API routes return 200 with stubbed data locally.
- QStash publish/consume verified in dev (log-only worker).
- Supabase tables created; seed script inserts without errors.
- Scraper test suite passes on golden pages; normalized outputs include base units.
- Frontend stub posts budget/city and renders response payload.

## Verification
- `pytest` in `backend/` passes (scraper + helpers).
- Manual curl: `curl -X POST localhost:8000/api/meal-plan -d '{"budget":50,"currency":"EUR","city":"vienna"}'` returns stub plan.
- Logs show `scrape_prices` and `plan_meals` messages with job_id and pricing_version.
- Seeded products visible in Supabase console.
