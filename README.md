# NutriWallet

> **Budget-first meal planning** that optimizes nutrition within your budget and city.

**The Problem:** Traditional meal planners start with calories/macros, then maybe consider cost.  
**Our Solution:** Start with your budget, optimize nutrition, then source ingredients.

---

## 🎯 Core Concept

**Invert the typical meal planning flow:**

```
Traditional: Calories/Macros → Food → (maybe) Cost
NutriWallet: Budget → Optimize Nutrition → Source Ingredients
```

**Example:** *"Eat the healthiest you can for €50/week in Vienna"* — tangible, budget-constrained, real problem.

---

## ✨ Features

- **Budget-first optimization** — Maximize protein/nutrition within your budget constraint
- **Multi-store price comparison** — Real-time pricing from SPAR, Tesco, BigBasket, Walmart
- **Location-specific** — Tailored to your city (Vienna, London, Mumbai, US cities)
- **AI-powered** — Agentic architecture for price discovery and meal synthesis
- **Linear programming** — Mathematical optimization for optimal meal plans

---

## 🏗️ Project Status

**Current Phase:** Early planning and task breakdown

- ✅ Architecture design complete
- ✅ MVP scope defined
- 🔄 Backend/frontend scaffolds in progress
- 📋 Week-by-week implementation plan (`tasks/`)

> **Note:** See `tasks/` for week-by-week work breakdown.

---

## 🛠️ Tech Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (async, modern)
- **Database:** PostgreSQL/Supabase
- **Queue:** QStash (hosted) or Celery (self-hosted)
- **Optimization:** PuLP for linear programming
- **Scraping:** Crawl4AI + Jina Reader (selector-first parsers with LLM fallback)

### Frontend
- **Framework:** Next.js 14+ (SSR, fast)
- **Styling:** Tailwind CSS
- **State:** Zustand
- **Forms:** React Hook Form

### Infrastructure
- **Hosting:** Railway/Render (backend), Vercel (frontend)
- **Database:** Supabase (free tier)
- **Cron Jobs:** Railway/GitHub Actions

---

## 📁 Project Structure

```
NutriWallet/
├── tasks/              # Week-by-week implementation plans
│   ├── week_1.md
│   └── week_2.md
├── docs/               # Architecture & MVP docs (local, git-ignored)
│   ├── MVP.md
│   └── TECHNICAL_ARCHITECTURE.md
├── AGENTS.md           # Contributor guide (local, git-ignored)
│
├── backend/            # FastAPI backend (coming soon)
│   ├── app/
│   │   ├── agents/     # Orchestrator, Researcher, Optimizer, Reporter
│   │   ├── scrapers/   # Store-specific scrapers
│   │   ├── db/         # Models, repository, migrations
│   │   └── api/        # Routes & schemas
│   └── tasks/          # Celery tasks for scheduled scraping
│
├── frontend/           # Next.js app (coming soon)
│   └── src/
│
└── scripts/            # Seed data & manual scrape triggers
```

---

## 🚀 Quick Start (Coming Soon)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 🌍 Supported Markets

| Market | Stores | Status |
|--------|--------|--------|
| 🇦🇹 Austria | SPAR, Billa, Hofer | Validated |
| 🇬🇧 UK | Tesco | Validated |
| 🇮🇳 India | BigBasket | Validated |
| 🇺🇸 USA | Walmart | Validated |

---

## 📚 Documentation

- **[Week-by-Week Tasks](tasks/)** — Implementation roadmap

---


## 📄 License

*License TBD*

