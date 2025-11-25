# Week 1 — Agent Foundation + Price Discovery

## Goals
- Set up the core agent architecture (Orchestrator + Researcher Agent)
- Implement price discovery with Crawl4AI (bypasses Cloudflare protection)
- Deploy Supabase schema and seed product list
- FastAPI skeleton with basic endpoints

## Tasks

### 1. Backend Scaffold
- FastAPI app with health check, `/api/meal-plan`, `/api/prices` endpoints
- Pydantic schemas for requests/responses
- Environment config:
  - `OPENAI_API_KEY` (for LLM parsing)
  - `SUPABASE_URL` (project URL)
  - `SUPABASE_SECRET_KEY` (sb_secret_... - server-side only)
- Structured logging with job_id, store, city

### 2. Agent Architecture Setup
- **Orchestrator Agent**: Receives user request (budget, city, preferences), coordinates sub-agents
- **Researcher Agent**: 
  - Uses Crawl4AI for web scraping (bypasses Cloudflare protection)
  - LLM parsing (OpenAI) to extract structured price data from markdown
- Agent communication pattern: Orchestrator → Researcher → return prices

### 3. Price Discovery Implementation
- Crawl4AI setup: `pip install crawl4ai && crawl4ai-setup`
- Browser-based scraping with headless Playwright
- LLM extraction prompt: Parse product name, price, unit, store from markdown
- Normalize units (kg, L, piece, 100g) to base units

### 4. Database Setup (Supabase)
- Apply schema: `products`, `prices`, `nutrition`, `scrape_jobs` tables
- Add normalization fields: `package_size`, `normalized_quantity`, `price_per_unit`
- Seed MVP product list (protein, carbs, vegetables, fats categories)
- Test queries for price lookups by city/category

### 5. SPAR Vienna Scraper (First Store)
- Selector-first parsing with CSS selectors
- LLM fallback only when selectors fail
- Store HTML/markdown snapshots for debugging
- Golden page fixtures (~10 items) for testing

### 6. Tests
- Unit tests for Researcher Agent (mock Crawl4AI responses)
- Golden-page fixtures for SPAR parser
- Normalization helper tests (unit parsing, price_per_unit calculation)

## Checkpoints
- [ ] Orchestrator receives request and calls Researcher Agent
- [ ] Researcher fetches prices via Crawl4AI successfully
- [ ] LLM parses markdown into structured price data
- [ ] Supabase tables created; seed script runs without errors
- [ ] SPAR scraper test suite passes on golden pages
- [ ] API routes return 200 with real (not stubbed) price data

## Verification
- `pytest backend/` passes (agents + scraper + helpers)
- Manual test: Researcher Agent fetches chicken breast price from SPAR Vienna
- Logs show agent handoff: `orchestrator → researcher → prices returned`
- Seeded products visible in Supabase console

## Architecture Alignment
```
Week 1 Focus:
┌─────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR ✅                      │
│         (Takes budget + city + dietary prefs)           │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌───────────────┐           ┌───────────────┐
│  RESEARCHER ✅ │           │   OPTIMIZER   │
│    AGENT      │           │   (Week 2)    │
│               │           │               │
│ • Crawl4AI    │           │               │
│ • LLM Parse   │           │               │
└───────────────┘           └───────────────┘
```
