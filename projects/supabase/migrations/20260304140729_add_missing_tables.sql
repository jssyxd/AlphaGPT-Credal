-- Add missing tables to existing Supabase database

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Daily reports table
CREATE TABLE IF NOT EXISTS daily_reports (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    total_pnl REAL DEFAULT 0,
    trade_count INT DEFAULT 0,
    win_count INT DEFAULT 0,
    loss_count INT DEFAULT 0,
    active_positions INT DEFAULT 0,
    total_volume REAL DEFAULT 0,
    best_trade REAL DEFAULT 0,
    worst_trade REAL DEFAULT 0,
    report_json JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- LLM logs table
CREATE TABLE IF NOT EXISTS llm_logs (
    id SERIAL PRIMARY KEY,
    prompt TEXT NOT NULL,
    response TEXT,
    model TEXT,
    tokens_used INT,
    cost REAL,
    status TEXT,
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default settings
INSERT INTO settings (key, value) VALUES
    ('mode', 'paper'),
    ('max_position_size_pct', '0.01'),
    ('max_positions', '3'),
    ('min_liquidity', '10000'),
    ('stop_loss_pct', '0.05'),
    ('take_profit_pct', '0.10'),
    ('trailing_stop_pct', '0.08'),
    ('min_holders', '50'),
    ('max_creator_percent', '20')
ON CONFLICT (key) DO NOTHING;

-- Add missing columns to existing tokens table
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS liquidity REAL DEFAULT 0;
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS holders INT DEFAULT 0;
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS creator_percent REAL DEFAULT 0;
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS price REAL DEFAULT 0;
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS price_change_24h REAL DEFAULT 0;
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS fdv REAL DEFAULT 0;
