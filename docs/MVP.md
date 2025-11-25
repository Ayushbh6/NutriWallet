# Budget-First Meal Planner — Project Brief

## The Core Idea

**Invert the typical meal planning flow.**

Traditional apps: `Calories/Macros → Food → (maybe) Cost`

Our approach: `Budget → Optimize Nutrition → Source Ingredients`

### Value Proposition
"Eat the healthiest you can for €50/week in Vienna" — tangible, budget-constrained, real problem.

### Target Users
- Students
- Young professionals
- Budget-conscious families
- Anyone who grocery budgets but has no app that *starts* there

---

## What Makes This Different

Every existing meal planner treats budget as a secondary filter. We make it the **primary input**.

The app takes:
- A weekly/monthly budget
- User's city/location
- Dietary preferences (optional)

And outputs:
- Optimized meal plan (maximizing protein/nutrition within budget constraint)
- Shopping list with best prices found
- Sources/links to where to buy

This is an **AI-native problem** — requires optimization + real-time market data + meal synthesis. Perfect for an agentic system.

---

## Competitive Landscape

### Direct Competitors

| App | What It Does | Gap |
|-----|--------------|-----|
| **Plateful** (Apr 2025) | Real-time pricing from 12+ US stores, budget tracking | Tracks spending, doesn't *generate* plans from budget |
| **Eat This Much** | AI meal planning with budget as secondary filter | Calories-first, budget is afterthought |
| **Strongr Fastr** | Macro-optimized meal plans, claims to save money | Budget is incidental, not the input |
| **Mealime** | Meal planning + grocery lists | No price data, no budget optimization |
| **Prospre** | AI macro planning + Instacart integration | No budget-first approach |

### Key Insight
Nobody is doing `budget → optimize nutrition → source ingredients`. The linear programming angle (maximize protein subject to budget constraint) is genuinely underserved.

---

## Technical Approach

### The Data Problem

Getting real-time, location-specific grocery prices is the hard part. Options:

1. **Commercial Scraping APIs** — Companies like RealData API, FoodDataScrape already scrape Walmart, Target, Instacart, etc. Mostly US-focused.

2. **Open Source Scrapers** — Boozio (GitHub) scrapes UK supermarkets (Sainsbury's, Asda, Tesco, Waitrose, Ocado, Morrisons)

3. **Agentic Web Search** — Breadth-first web searches to find prices from search snippets and fetched pages. Won't be perfect, but "good enough" for MVP.

### Our Approach: Agentic Architecture

Instead of building/maintaining scrapers for every store, use AI agents to:
- Search broadly for ingredient prices in the user's city
- Extract structured price data from search results
- Handle the messiness with LLM parsing

This is scrappy but validates faster than building perfect infrastructure.

---

## MVP Architecture

### Agent Stack (Minimal Viable Version)

```
┌─────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                        │
│         (Takes budget + city + dietary prefs)           │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌───────────────┐           ┌───────────────┐
│  RESEARCHER   │           │   OPTIMIZER   │
│    AGENT      │           │               │
│               │           │ Linear optim: │
│ • Web search  │──────────▶│ max protein   │
│ • Price hunt  │  prices   │ s.t. budget   │
│ • Deal finder │           │               │
└───────────────┘           └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │   REPORTER    │
                            │               │
                            │ • Meal plan   │
                            │ • Shopping    │
                            │   list        │
                            │ • Sources     │
                            └───────────────┘
```

### Tech Stack (Suggested)
- **Frontend**: Next.js (you know it well from Merlin)
- **Backend**: Python or Node.js agent framework
- **Queue**: Redis + BullMQ for async price searches
- **Database**: MongoDB or Postgres for caching prices
- **LLM**: Claude API for parsing/reasoning

### MVP Scope
- Single city to start (Vienna or a US city with better data)
- Weekly meal plan output
- Basic protein/calorie optimization
- Web search-based price discovery (not perfect scrapers)
- Simple UI — input budget, get plan

---

## Build in Public Strategy

### Week 1: Ship Ugly MVP
- Get core agent loop working
- Basic UI (doesn't need to be pretty)
- Record a Loom demo showing it in action

### Launch Channels
- **Twitter/X**: Thread explaining the idea + demo video
- **Reddit**: 
  - r/EatCheapAndHealthy
  - r/mealprep
  - r/Frugal
  - r/SideProject
  - r/IndieHackers
- **Hacker News**: "Show HN" post — this is exactly what HN loves (agentic AI, practical problem, solo builder)
- **Indie Hackers**: Post in the community

### What to Track
- Do people actually use the generated plans?
- Is the price data "good enough"?
- What's the #1 complaint?
- Would anyone pay for this?

---

## Known Challenges

### 1. Location-Specific Data
Austrian grocery sites (Billa, Spar, Hofer) might be harder to get search results for than US stores. 

**Mitigation**: Start US-first where data is abundant, or manually seed some Austrian price knowledge.

### 2. Search Result Quality
Web search snippets won't give perfect prices. LLM parsing will have errors.

**Mitigation**: "Approximately right" is fine for MVP. Validate if users care about precision.

### 3. Price Freshness
Grocery prices change. Weekly? Daily?

**Mitigation**: For MVP, weekly refresh is probably fine. Add freshness indicator to UI.

### 4. Legal Gray Area
Scraping is technically questionable for some sites.

**Mitigation**: For MVP, rely on web search (public info) rather than direct scraping. If it takes off, negotiate partnerships or use official APIs.

---

## Validation Checklist

Before scaling, validate these assumptions:

- [ ] Can you manually build a €50/week optimal meal plan for Vienna? (Do it by hand first)
- [ ] Do 5-10 test users actually follow the generated plans?
- [ ] Is "budget-first" actually the hook, or do people still think in calories?
- [ ] Would anyone pay €3-5/month for this?
- [ ] Is the agentic price search "good enough" or frustratingly wrong?

---

## Next Steps

1. **Decide starting market**: Vienna (home turf) or US (better data)?
2. **Sketch agent prompts**: What does the researcher agent actually search for?
3. **Build core loop**: Budget in → meal plan out (ugly is fine)
4. **Test on yourself**: Use it for a week
5. **Ship and post**: Get it in front of real users

---

## Resources Found

### Existing Apps to Study
- [Plateful](https://www.platefulapp.com/) — Real-time grocery pricing
- [Eat This Much](https://www.eatthismuch.com/) — Automatic meal planner
- [Strongr Fastr](https://www.strongrfastr.com/) — Macro meal planning

### Technical Resources
- [Boozio UK Supermarket Scraper](https://github.com/ciarans/Boozio-UK-Supermarket-Scraper) — Open source price scraping
- [RealData API](https://www.realdataapi.com/grocery-data-scraping.php) — Commercial grocery scraping
- [FoodDataScrape](https://www.fooddatascrape.com/) — Grocery delivery data API

### Communities for Launch
- r/EatCheapAndHealthy (2.5M+ members)
- r/mealprep (1.5M+ members)
- r/Frugal (2M+ members)
- Indie Hackers
- Hacker News (Show HN)

---

## Project Codename Ideas
- BudgetBite
- MealMath
- FrugalFuel
- NutriWallet
- SmartPlate

---

*Document generated: November 2025*
*Status: Ideation → MVP Build*