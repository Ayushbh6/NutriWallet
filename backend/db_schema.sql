-- NutriWallet Database Schema
-- Execute this in your Supabase SQL Editor

-- Products table (scraped items)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,  -- "chicken breast" not "SPAR Hühnerbrust"
    category TEXT NOT NULL,         -- protein, carbs, vegetables, dairy, fats
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Prices table (price observations)
CREATE TABLE IF NOT EXISTS prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
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
CREATE TABLE IF NOT EXISTS nutrition (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    calories_per_100g INTEGER,
    protein_per_100g DECIMAL(5,2),
    carbs_per_100g DECIMAL(5,2),
    fat_per_100g DECIMAL(5,2),
    fiber_per_100g DECIMAL(5,2)
);

-- Scrape jobs (tracking)
CREATE TABLE IF NOT EXISTS scrape_jobs (
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
CREATE INDEX IF NOT EXISTS idx_prices_store_city ON prices(store, city);
CREATE INDEX IF NOT EXISTS idx_prices_product_scraped ON prices(product_id, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_normalized_name ON products(normalized_name);
CREATE INDEX IF NOT EXISTS idx_scrape_jobs_status ON scrape_jobs(status, started_at DESC);

