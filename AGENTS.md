# Repository Guidelines

## Project Structure & Modules
- Root: `docs/` (architecture, MVP), `backend/` (FastAPI, agents, scrapers, DB, tasks), `frontend/` (Next.js app), `scripts/` (seed/run helpers), `docker-compose.yml`.
- Backend layout highlights: `app/agents/` (orchestrator, researcher, optimizer, reporter), `app/scrapers/` (store-specific), `app/db/` (models, repository, migrations), `app/services/` (price + meal logic), `app/api/` (routes, schemas), `tasks/` (Celery).
- Tests live under `backend/tests/`; add store fixtures/golden pages for scrapers.

## Build, Test, Run
- Backend install: `cd backend && pip install -r requirements.txt`.
- Run API locally: `uvicorn app.main:app --reload` (FastAPI dev server).
- Task worker: `celery -A tasks.celery_app worker --loglevel=info`.
- Scheduled scrape (manual): `python scripts/run_scrape.py --store spar --city vienna`.
- Frontend install/run: `cd frontend && npm install && npm run dev`.

## Coding Style & Naming
- Python: PEP 8, type hints where useful; prefer async for I/O. Modules snake_case; classes PascalCase; functions/vars snake_case. Keep scrapers deterministic before LLM fallbacks.
- JS/TS: 2-space indent; React components PascalCase; hooks start with `use*`; state stores in `frontend/src/lib` or `state` folder.
- Lint/format: use `black`/`isort` for Python; `eslint`/`prettier` for frontend (run via package scripts if present).

## Testing Guidelines
- Backend tests: `pytest` from `backend/`; name tests `test_*.py`. Add golden HTML snapshots for scraper parsers and assert normalized units/prices. For optimizer, include synthetic budget feasibility cases.
- Frontend tests (if added): `npm test` or `npm run lint`; co-locate component tests under `__tests__` or `*.test.tsx`.

## Commit & PR Guidelines
- Commits: concise imperative subject ("Add SPAR scraper parser"), scoped changes; group related edits.
- PRs: describe scope, linked issues, how to test, and screenshots for UI changes. Note data sources touched, selector version bumps (`pricing_version`), and any new env vars. Ensure tests pass before requesting review.

## Security & Configuration Tips
- Store secrets in env files, not VCS. Rotate User-Agent/proxy configs per store; honor robots/ToS. Rate-limit `/api/scrape/trigger` and capture scrape/optimizer logs with job IDs.
