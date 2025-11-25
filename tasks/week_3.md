# Week 3 — Reporter Agent + Full Pipeline

## Goals
- Implement the Reporter Agent for meal plan generation
- Complete end-to-end agent pipeline (Orchestrator → Researcher → Optimizer → Reporter)
- Add Billa/Hofer (Austria) and Walmart (USA) scrapers
- Meal plan output with shopping list and store links

## Tasks

### 1. Reporter Agent Implementation
- **Meal Plan Generation**:
  - Take optimized ingredients from Optimizer
  - Generate 7-day meal plan (breakfast, lunch, dinner)
  - Use LLM (OpenAI) to create realistic meal combinations
  - Respect dietary preferences (vegetarian, vegan, etc.)
- **Shopping List Assembly**:
  - Aggregate ingredients across all meals
  - Include quantities with normalized units
  - Add `price_per_unit` and total cost per item
  - Sort by store for efficient shopping
- **Store Links**:
  - Include original product URLs from scraping
  - Group items by store
  - Show cheapest option when multiple stores have same item

### 2. Additional Scrapers
- **Billa (Austria)**: Selector-first parser, golden pages, tests
- **Hofer (Austria)**: Selector-first parser, golden pages, tests
- **Walmart (USA)**: Selector-first parser, golden pages, tests
- Update scheduled scraping:
  - Billa/Hofer: Weekly
  - Walmart: Daily (more dynamic pricing)

### 3. Full Agent Pipeline
- Complete flow: `User Request → Orchestrator → Researcher → Optimizer → Reporter → Response`
- Error handling at each stage:
  - Researcher fails: Return cached prices or error message
  - Optimizer infeasible: Reporter explains why and suggests alternatives
  - Reporter fails: Return raw optimized list without meal formatting
- Logging with full trace: job_id flows through all agents

### 4. Nutritional Summary
- Calculate totals per day and per week:
  - Calories, Protein, Carbs, Fat, Fiber
- Compare against targets (e.g., 150g protein/day goal)
- Show percentage of target met
- Use nutrition data from seeded `nutrition` table

### 5. Data Provenance
- Track `source_type` for each price: `crawl4ai`, `cached`
- Show `last_updated` timestamp in output
- Flag stale data (beyond SLA) with warning
- Include `confidence` score for LLM-parsed prices

### 6. Tests
- Reporter Agent unit tests:
  - Valid meal plan generation
  - Shopping list aggregation
  - Nutritional calculation accuracy
- Integration test: Full pipeline from budget input to meal plan output
- End-to-end test with real (cached) price data

## Checkpoints
- [ ] Reporter generates valid 7-day meal plan from optimized ingredients
- [ ] Shopping list includes all items with prices and store links
- [ ] Nutritional summary shows daily/weekly totals
- [ ] Full pipeline: €50 Vienna request → complete meal plan response
- [ ] Billa, Hofer, Walmart scrapers pass tests
- [ ] Error handling works: infeasible budget returns helpful message

## Verification
- `pytest backend/` covers all agents, scrapers, full pipeline
- Manual test: POST `/api/meal-plan` with €50/Vienna returns complete plan
- Response includes: meals array, shopping_list, total_cost, nutritional_summary
- Logs show full trace: `orchestrator → researcher → optimizer → reporter`

## Architecture Alignment
```
Week 3 Focus — COMPLETE PIPELINE:
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
│               │           │ Linear optim: │
│ • 6 stores    │──────────▶│ max protein   │
│ • Scheduled   │  prices   │ s.t. budget   │
└───────────────┘           └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  REPORTER ✅   │
                            │               │
                            │ • Meal plan   │
                            │ • Shopping    │
                            │   list        │
                            │ • Nutrition   │
                            │ • Sources     │
                            └───────────────┘
```

