# NutriWallet Backend

Backend API for NutriWallet - Budget-first meal planning application.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Crawl4AI Browser

```bash
crawl4ai-setup
```

This installs Playwright browsers needed for Crawl4AI.

### 3. Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=sb_secret_your_secret_key_here
LOG_LEVEL=INFO
```

### 4. Database Setup

Execute the SQL schema in your Supabase dashboard:

```bash
# Copy the SQL from db_schema.sql and run it in Supabase SQL Editor
```

### 5. Seed Products

```bash
python scripts/seed_products.py
```

## Running the API

### Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── agents/          # AI agents (Orchestrator, Researcher)
│   ├── api/             # FastAPI routes and schemas
│   ├── db/              # Supabase client and repository
│   ├── scrapers/        # Web scrapers (Jina, Crawl4AI, stores)
│   ├── services/        # Business logic (price normalization)
│   ├── config.py        # Configuration
│   └── main.py          # FastAPI app entry point
├── tests/               # Test suite
├── scripts/             # Utility scripts
└── requirements.txt     # Python dependencies
```

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Prices
- `GET /api/prices?city=vienna&category=protein` - Get prices (Week 1: stub)

### Meal Plan
- `POST /api/meal-plan` - Generate meal plan (Week 1: stub, Week 2: full implementation)

## Week 1 Status

✅ Backend scaffold complete
✅ Agent architecture (Orchestrator + Researcher)
✅ Price discovery with Crawl4AI (bypasses Cloudflare protection)
✅ Supabase schema and repository
✅ Price normalization service
✅ SPAR Vienna scraper (basic)
✅ Test suite foundation

## Next Steps (Week 2)

- Integrate Researcher Agent with price API endpoint
- Implement web search for product URLs
- Add more store scrapers (Tesco, BigBasket)
- Scheduled scraping with Celery

