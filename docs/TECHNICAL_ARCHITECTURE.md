# NutriWallet — Technical Architecture

## Overview

This document outlines the technical architecture for NutriWallet, a budget-first meal planning application that optimizes nutrition within a user's budget constraint.

**Core Flow:** `Budget → Optimize Nutrition → Source Ingredients`

---

## Validated Markets

| Market | Store | Data Quality | Status |
|--------|-------|--------------|--------|
| 🇦🇹 Austria | SPAR, Billa, Hofer | ✅ Excellent | Validated |
| 🇺🇸 USA | Walmart | ✅ Good | Validated |
| 🇬🇧 UK | Tesco | ✅ Excellent | Validated |
| 🇮🇳 India | BigBasket | ✅ Excellent | Validated |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                               │
│                    (Next.js / React Frontend)                          │
│         Budget Input → City Selection → Dietary Preferences            │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR AGENT                             │
│                           (OpenAI API)                                 │
│                                                                        │
│   • Receives user request (budget, city, preferences)                 │
│   • Coordinates sub-agents                                            │
│   • Assembles final meal plan                                         │
└───────────┬─────────────────────────────────┬──────────────────────────┘
            │                                 │
            ▼                                 ▼
┌───────────────────────┐         ┌──────────────────────────────────────┐
│   RESEARCHER AGENT    │         │          OPTIMIZER AGENT             │
│                       │         │                                      │
│ PRIMARY: Agentic      │         │ • Linear programming                 │
│   Web Search          │         │ • Maximize: protein/nutrition        │
│                       │ ──────▶ │ • Subject to: budget constraint      │
│ FALLBACK: Price       │ prices  │ • Constraints: variety, meal types   │
│   Repository (DB)     │         │                                      │
└───────────┬───────────┘         └───────────────────┬──────────────────┘
            │                                         │
            ▼                                         ▼
┌───────────────────────┐                 ┌───────────────────────┐
│   PRICE REPOSITORY    │                 │    REPORTER AGENT     │
│      (Postgres)       │                 │                       │
│                       │                 │ • Generates meal plan │
│ • Cached prices       │                 │ • Shopping list       │
│ • Updated via         │                 │ • Store links         │
│   scheduled scraping  │                 │ • Nutritional summary │
│ • 7-day freshness     │                 │                       │
└───────────────────────┘                 └───────────────────────┘
```

---

## Data Layer: Dual-Source Strategy

### Why Dual-Source?

1. **Agentic Search (Primary):** Real-time, always fresh, but can fail
2. **Price Repository (Fallback):** Reliable, fast, but may be slightly stale

Grocery prices don't change daily — weekly updates are sufficient for MVP.

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA ACQUISITION LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   ┌─────────────────────┐      ┌─────────────────────────────────────┐ │
│   │  REAL-TIME PATH     │      │      SCHEDULED SCRAPING PATH        │ │
│   │  (On User Request)  │      │      (Background Job)               │ │
│   │                     │      │                                     │ │
│   │  User Request       │      │  Cron Job (Weekly)                  │ │
│   │       │             │      │       │                             │ │
│   │       ▼             │      │       ▼                             │ │
│   │  ┌─────────────┐    │      │  ┌─────────────────────────────┐   │ │
│   │  │ Jina Reader │    │      │  │      Crawl4AI               │   │ │
│   │  │ (Fast,Free) │    │      │  │  (Full scraper, async)      │   │ │
│   │  └──────┬──────┘    │      │  └──────────────┬──────────────┘   │ │
│   │         │           │      │                 │                  │ │
│   │         ▼           │      │                 ▼                  │ │
│   │  ┌─────────────┐    │      │  ┌─────────────────────────────┐   │ │
│   │  │ LLM Parse   │    │      │  │   Structured Extraction     │   │ │
│   │  │ (OpenAI API)│    │      │  │   (CSS + LLM Hybrid)        │   │ │
│   │  └──────┬──────┘    │      │  └──────────────┬──────────────┘   │ │
│   │         │           │      │                 │                  │ │
│   │         ▼           │      │                 ▼                  │ │
│   │  Return to User     │      │  ┌─────────────────────────────┐   │ │
│   │  + Cache in DB      │      │  │   Price Repository (DB)     │   │ │
│   │                     │      │  │   • product_name            │   │ │
│   └─────────────────────┘      │  │   • price                   │   │ │
│                                │  │   • unit (kg, L, piece)     │   │ │
│                                │  │   • store                   │   │ │
│                                │  │   • city                    │   │ │
│                                │  │   • scraped_at              │   │ │
│                                │  │   • url                     │   │ │
│                                │  └─────────────────────────────┘   │ │
│                                └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Web Scraping Stack

### Primary Tool: Crawl4AI (FREE, Open Source)

**Why Crawl4AI?**
- 56k+ GitHub stars (#1 trending)
- 100% free, no API keys needed
- Async browser pool (fast)
- LLM-ready markdown output
- Supports scheduled scraping
- Self-hosted = full control

**Installation:**
```bash
pip install -U crawl4ai
crawl4ai-setup  # Installs Playwright browsers
```

**Basic Usage:**
```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def scrape_prices(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                word_count_threshold=1,
                page_timeout=30000,
            )
        )
        return result.markdown  # Clean, LLM-ready output
```

### Fallback Tool: Jina Reader (FREE, Simple)

For quick, single-page extractions:
```python
import requests

def quick_scrape(url: str) -> str:
    """Prepend r.jina.ai/ to any URL for instant markdown"""
    jina_url = f"https://r.jina.ai/{url}"
    response = requests.get(jina_url)
    return response.text
```

### Tool Comparison

| Feature | Crawl4AI | Jina Reader | Firecrawl |
|---------|----------|-------------|-----------|
| Cost | FREE | FREE | $16+/mo |
| Self-hosted | ✅ | ❌ | Partial |
| Async/Batch | ✅ | ❌ | ✅ |
| JS Rendering | ✅ | ✅ | ✅ |
| Scheduled Jobs | ✅ | ❌ | ✅ |
| Best For | Bulk scraping | Quick lookups | Cloud API |

---

## Database Schema

### PostgreSQL (via Supabase)

```sql
-- Products table (scraped items)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,  -- "chicken breast" not "SPAR Hühnerbrust"
    category TEXT NOT NULL,         -- protein, carbs, vegetables, dairy, etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Prices table (price observations)
CREATE TABLE prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    store TEXT NOT NULL,            -- spar, billa, walmart, tesco, bigbasket
    city TEXT NOT NULL,             -- vienna, london, mumbai, etc.
    country TEXT NOT NULL,          -- AT, US, UK, IN
    price DECIMAL(10,2) NOT NULL,
    currency TEXT NOT NULL,         -- EUR, USD, GBP, INR
    unit TEXT NOT NULL,             -- kg, L, piece, 100g
    price_per_unit DECIMAL(10,2),   -- normalized price per kg/L
    original_url TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    is_on_sale BOOLEAN DEFAULT FALSE,
    sale_price DECIMAL(10,2)
);

-- Nutritional data (static, seeded once)
CREATE TABLE nutrition (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    calories_per_100g INTEGER,
    protein_per_100g DECIMAL(5,2),
    carbs_per_100g DECIMAL(5,2),
    fat_per_100g DECIMAL(5,2),
    fiber_per_100g DECIMAL(5,2)
);

-- Scrape jobs (tracking)
CREATE TABLE scrape_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store TEXT NOT NULL,
    city TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, running, completed, failed
    items_scraped INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

-- Indexes for fast lookups
CREATE INDEX idx_prices_store_city ON prices(store, city);
CREATE INDEX idx_prices_product_scraped ON prices(product_id, scraped_at DESC);
CREATE INDEX idx_products_category ON products(category);
```

---

## Scheduled Scraping Strategy

### Scrape Frequency

| Store Type | Frequency | Reason |
|------------|-----------|--------|
| Supermarkets | Weekly | Prices change with weekly flyers |
| Discount stores | 2x/week | Flash sales more common |
| Online-only | Daily | More dynamic pricing |

### Cron Schedule (Example)

```bash
# Weekly scrape - Sunday 2 AM (before new week's prices)
0 2 * * 0 /path/to/scrape_all_stores.py

# Mid-week update for discount stores
0 2 * * 3 /path/to/scrape_discount_stores.py
```

### Scraping Priority List (MVP)

**Phase 1 (Week 1):**
- Austria: SPAR (spar.at)
- UK: Tesco (tesco.com)

**Phase 2 (Week 2):**
- India: BigBasket (bigbasket.com)
- Austria: Billa, Hofer

**Phase 3 (Week 3):**
- USA: Walmart (walmart.com)
- UK: Sainsbury's, Asda

### Products to Scrape (MVP - High Protein Focus)

```python
MVP_PRODUCTS = {
    "protein": [
        "chicken breast",
        "eggs",
        "greek yogurt",
        "cottage cheese",
        "tofu",
        "lentils",
        "chickpeas",
        "tuna",
        "ground beef",
        "milk",
    ],
    "carbs": [
        "rice",
        "oats",
        "bread",
        "pasta",
        "potatoes",
        "bananas",
    ],
    "vegetables": [
        "broccoli",
        "spinach",
        "carrots",
        "onions",
        "tomatoes",
    ],
    "fats": [
        "olive oil",
        "peanut butter",
        "butter",
    ],
}
```

---

## Tech Stack Summary

### Backend
| Component | Technology | Why |
|-----------|------------|-----|
| Language | Python 3.11+ | Best for AI/ML, scraping |
| Web Framework | FastAPI | Async, fast, modern |
| Scraping | Crawl4AI | Free, powerful, LLM-ready |
| Quick Scrape | Jina Reader | Simple fallback |
| Database | PostgreSQL (Supabase) | Reliable, free tier |
| Task Queue | Redis + Celery | Scheduled scraping |
| LLM | OpenAI API | Primary model provider (framework TBD, e.g. OpenAI Agents / PydanticAI) |

### Frontend
| Component | Technology | Why |
|-----------|------------|-----|
| Framework | Next.js 14+ | SSR, fast, familiar |
| Styling | Tailwind CSS | Rapid UI development |
| State | Zustand | Simple, lightweight |
| Forms | React Hook Form | Easy validation |

### Infrastructure
| Component | Technology | Why |
|-----------|------------|-----|
| Hosting (Backend) | Railway / Render | Easy Python deployment |
| Hosting (Frontend) | Vercel | Next.js native |
| Database | Supabase | Free tier, Postgres |
| Cron Jobs | Railway / GitHub Actions | Free scheduled tasks |

---

## API Endpoints (MVP)

```
POST /api/meal-plan
  Body: { budget: 50, currency: "EUR", city: "vienna", preferences: {...} }
  Returns: { meals: [...], shopping_list: [...], total_cost: 48.50 }

GET /api/prices?city=vienna&category=protein
  Returns: [{ product: "chicken breast", price: 8.99, store: "spar", ... }]

GET /api/stores?city=vienna
  Returns: [{ name: "SPAR", url: "spar.at" }, ...]

POST /api/scrape/trigger  (admin only)
  Body: { store: "spar", city: "vienna" }
  Returns: { job_id: "...", status: "started" }
```

---

## Project Structure

```
NutriWallet/
├── docs/
│   ├── MVP.md
│   └── TECHNICAL_ARCHITECTURE.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Environment config
│   │   ├── agents/
│   │   │   ├── orchestrator.py  # Main coordinator
│   │   │   ├── researcher.py    # Price fetching
│   │   │   ├── optimizer.py     # Meal optimization
│   │   │   └── reporter.py      # Output formatting
│   │   ├── scrapers/
│   │   │   ├── base.py          # Base scraper class
│   │   │   ├── crawl4ai_scraper.py
│   │   │   ├── jina_scraper.py
│   │   │   └── stores/
│   │   │       ├── spar.py
│   │   │       ├── tesco.py
│   │   │       ├── bigbasket.py
│   │   │       └── walmart.py
│   │   ├── db/
│   │   │   ├── models.py        # SQLAlchemy models
│   │   │   ├── repository.py    # DB operations
│   │   │   └── migrations/
│   │   ├── services/
│   │   │   ├── price_service.py
│   │   │   └── meal_planner.py
│   │   └── api/
│   │       ├── routes.py
│   │       └── schemas.py       # Pydantic models
│   ├── tasks/
│   │   ├── celery_app.py
│   │   └── scrape_tasks.py      # Scheduled scraping
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── next.config.js
├── scripts/
│   ├── seed_products.py         # Initial product list
│   └── run_scrape.py            # Manual scrape trigger
└── docker-compose.yml
```

---

## Implementation Phases

### Phase 1: Price Fetcher POC (Week 1)
- [ ] Set up Python backend with FastAPI
- [ ] Implement Crawl4AI scraper for SPAR Vienna
- [ ] Create basic price repository (Supabase)
- [ ] Test: Fetch 10 products, store prices

### Phase 2: Multi-Store Scraping (Week 2)
- [ ] Add Tesco (UK) scraper
- [ ] Add BigBasket (India) scraper
- [ ] Implement scheduled scraping (cron)
- [ ] Build price comparison API

### Phase 3: Optimization Engine (Week 3)
- [ ] Implement linear programming optimizer
- [ ] Create meal plan generator
- [ ] Add nutritional constraints
- [ ] Test with real price data

### Phase 4: Frontend MVP (Week 4)
- [ ] Build Next.js frontend
- [ ] Budget input UI
- [ ] Meal plan display
- [ ] Shopping list with store links

### Phase 5: Launch (Week 5)
- [ ] Deploy to production
- [ ] Create demo video
- [ ] Post on Reddit, HN, Twitter
- [ ] Collect feedback

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Scraping blocked | Use Crawl4AI's proxy rotation, respect rate limits |
| Prices stale | Show "last updated" timestamp, refresh on demand |
| LLM costs high | Use local models (Ollama) for parsing, OpenAI only for complex tasks |
| Store layout changes | CSS selectors break → fall back to LLM extraction |
| Legal concerns | Only scrape public data, cache locally, don't redistribute raw data |

---

## Success Metrics (MVP)

- [ ] Successfully scrape 50+ products from 4 stores
- [ ] Generate a valid €50/week meal plan for Vienna
- [ ] < 30 second response time for meal plan generation
- [ ] 5+ test users complete a full week using the plan
- [ ] At least 1 "would pay for this" response

