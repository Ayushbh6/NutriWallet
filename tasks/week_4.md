# Week 4 — Frontend MVP

## Goals
- Build Next.js frontend with budget-first UX
- Connect to backend API for real meal plans
- Display meal plan, shopping list, and nutritional info
- Polish UI with loading states, error handling, and responsive design

## Tasks

### 1. Next.js App Setup
- Next.js 14+ with App Router
- Tailwind CSS for styling
- Zustand for state management
- React Hook Form for input validation
- Environment config:
  - `NEXT_PUBLIC_API_URL` (backend API endpoint)
  - `NEXT_PUBLIC_SUPABASE_URL` (if direct DB access needed)
  - `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` (sb_publishable_... - client-safe)

### 2. Budget Input Page (Home)
- **Primary Input**: Weekly budget amount
- **Currency Selector**: EUR, USD, GBP, INR
- **City Selector**: Vienna, London, Mumbai, US cities
- **Dietary Preferences** (optional):
  - Vegetarian, Vegan, Pescatarian
  - Allergies (nuts, dairy, gluten)
  - Protein target slider
- **CTA Button**: "Generate My Meal Plan"
- Form validation with helpful error messages

### 3. Meal Plan Display Page
- **7-Day Calendar View**:
  - Each day shows Breakfast, Lunch, Dinner
  - Meal cards with name, ingredients, estimated calories
  - Click to expand for full recipe/ingredients
- **Summary Header**:
  - Total cost vs budget (with progress bar)
  - Weekly nutrition totals (protein, calories)
  - "Within budget" or "Over budget" indicator

### 4. Shopping List Component
- **Grouped by Store**:
  - SPAR items, Billa items, etc.
  - Each store section collapsible
- **Item Details**:
  - Product name, quantity, unit
  - Price and price_per_unit
  - "View in store" link (opens product URL)
- **Totals**:
  - Per-store subtotal
  - Grand total
  - Savings vs buying all at one store

### 5. Nutritional Summary Component
- Daily breakdown chart (bar chart or table)
- Weekly totals with target comparison
- Macros: Protein, Carbs, Fat, Fiber
- Calories per day average

### 6. UX Polish
- **Loading States**:
  - Skeleton loaders while fetching
  - Progress indicator for meal plan generation
  - Estimated wait time ("Usually takes 10-15 seconds")
- **Error Handling**:
  - API error: Friendly message + retry button
  - Infeasible budget: Explain why + suggest minimum
  - Network error: Offline indicator
- **Stale Data Warning**:
  - Show badge when prices are beyond SLA
  - "Prices last updated X days ago"
- **Responsive Design**:
  - Mobile-first approach
  - Works on phone, tablet, desktop

### 7. API Integration
- POST `/api/meal-plan` with budget, city, preferences
- GET `/api/prices` for price explorer (optional page)
- GET `/api/stores` for city/store dropdown population
- Handle API response structure from Reporter Agent

## Checkpoints
- [ ] Budget input form validates and submits successfully
- [ ] Meal plan displays 7 days with all meals
- [ ] Shopping list shows items grouped by store with links
- [ ] Nutritional summary displays accurate totals
- [ ] Loading states appear during API calls
- [ ] Error states display helpful messages
- [ ] Mobile responsive layout works

## Verification
- `npm run build` succeeds without errors
- Manual test: Enter €50/Vienna → See complete meal plan
- Click store links → Open correct product pages
- Test on mobile viewport → Layout works
- Test error: Disconnect API → See error message + retry

## UI/UX Guidelines
- **Budget-First**: Budget input is the hero, not hidden
- **Trust Signals**: Show "last updated" timestamps, data sources
- **Actionable**: Every screen has a clear next action
- **Fast Feedback**: Loading states, optimistic updates where possible
- **Accessible**: Proper contrast, keyboard navigation, screen reader friendly

## Architecture Alignment
```
Week 4 Focus:
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE ✅                              │
│                    (Next.js / React Frontend)                           │
│         Budget Input → City Selection → Dietary Preferences             │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR AGENT                              │
│                           (Backend API)                                 │
│                                                                         │
│   • Receives user request (budget, city, preferences)                  │
│   • Returns meal plan, shopping list, nutrition                        │
└─────────────────────────────────────────────────────────────────────────┘
```

