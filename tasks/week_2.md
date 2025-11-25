# Week 2 — Multi-Store Scraping + Optimizer Agent

## Goals
- Add Tesco (UK) and BigBasket (India) scrapers
- Implement the Optimizer Agent with PuLP linear programming
- Set up scheduled scraping with Celery + Redis
- Price comparison API with freshness tracking

## Tasks

### 1. Multi-Store Scrapers
- **Tesco (UK)**: Selector-first parser, golden page fixtures, tests
- **BigBasket (India)**: Selector-first parser, golden page fixtures, tests
- Store HTML/markdown snapshots for each store
- Expand product coverage to full MVP list

### 2. Optimizer Agent Implementation
- **PuLP linear programming solver**:
  - Objective: Maximize protein (or weighted nutrition score)
  - Subject to: Budget constraint (±2% tolerance)
  - Constraints:
    - Per-category maximums (e.g., max 3kg chicken/week)
    - Per-item max units (variety enforcement)
    - Minimum meal variety (at least N different proteins)
    - Calorie bounds (optional)
- Return feasibility codes: `optimal`, `infeasible`, `budget_too_low`
- Handle edge cases: empty price data, all items too expensive

### 3. Scheduled Scraping (Celery + Redis)
- Celery app setup with Redis broker
- Scrape tasks: `scrape_spar`, `scrape_tesco`, `scrape_bigbasket`
- Schedule per store SLA:
  - SPAR: Weekly (Sunday 2 AM)
  - Tesco: 2x/week (Sunday, Wednesday)
  - BigBasket: 2x/week
- Job tracking in `scrape_jobs` table

### 4. Price API Enhancement
- `/api/prices?city=&category=` with filters
- Include `last_updated`, `source_type`, `confidence` fields
- Freshness filter: Only return prices within SLA window
- Price comparison across stores for same product

### 5. Agent Pipeline Integration
- Orchestrator → Researcher → **Optimizer** flow
- Researcher passes normalized prices to Optimizer
- Optimizer returns optimized ingredient list with quantities
- Handle Optimizer failures gracefully (return partial results)

### 6. Tests
- Scraper tests for SPAR, Tesco, BigBasket (all pass)
- Optimizer unit tests:
  - Feasible budget scenario
  - Infeasible budget scenario (too low)
  - Edge case: single category available
  - Variety constraint enforcement
- Integration test: Researcher → Optimizer pipeline

## Checkpoints
- [ ] Tesco and BigBasket scrapers pass golden page tests
- [ ] Optimizer solves feasible €50/week Vienna scenario
- [ ] Optimizer returns `infeasible` for €10/week scenario
- [ ] Celery worker runs scheduled scrape task
- [ ] `/api/prices` returns filtered, fresh results with timestamps
- [ ] Orchestrator → Researcher → Optimizer pipeline works end-to-end

## Verification
- `pytest backend/` covers scrapers, normalization, optimizer
- Manual test: `/api/prices?city=vienna&category=protein` returns fresh data
- Optimizer test: €50 budget returns valid ingredient list meeting protein target
- Celery logs show scheduled job execution with job_id

## Architecture Alignment
```
Week 2 Focus:
┌─────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR ✅                      │
│         (Takes budget + city + dietary prefs)           │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌───────────────┐           ┌───────────────┐
│  RESEARCHER ✅ │           │  OPTIMIZER ✅  │
│    AGENT      │           │               │
│               │           │ • PuLP LP     │
│ • Multi-store │──────────▶│ • Max protein │
│ • Scheduled   │  prices   │ • Budget s.t. │
│               │           │ • Variety     │
└───────────────┘           └───────────────┘
```
