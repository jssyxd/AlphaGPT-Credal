-- Enhanced AlphaGPT Database Schema
-- Run in Supabase SQL Editor

-- 1. tokens: Token information with safety metrics
CREATE TABLE IF NOT EXISTS tokens (
    address TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    name TEXT,
    decimals INT DEFAULT 9,
    chain TEXT DEFAULT 'solana',
    liquidity REAL DEFAULT 0,
    holders INT DEFAULT 0,
    creator_percent REAL DEFAULT 0,
    price REAL DEFAULT 0,
    price_change_24h REAL DEFAULT 0,
    fdv REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. ohlcv: OHLCV data
CREATE TABLE IF NOT EXISTS ohlcv (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP NOT NULL,
    address TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    liquidity REAL,
    fdv REAL,
    source TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(time, address)
);

-- 3. strategies: Trading strategies/factors
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    formula TEXT NOT NULL,
    formula_json JSONB,
    score REAL DEFAULT 0,
    uncertainty REAL DEFAULT 1.0,
    backtest_result JSONB,
    performance_metrics JSONB,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. positions: Current and historical positions
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    token_address TEXT NOT NULL,
    symbol TEXT NOT NULL,
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP DEFAULT NOW(),
    amount_sol REAL NOT NULL,
    amount_tokens REAL,
    status TEXT DEFAULT 'open',
    exit_price REAL,
    exit_time TIMESTAMP,
    pnl REAL,
    pnl_percent REAL,
    stop_loss_price REAL,
    take_profit_price REAL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. trades: Complete trade history
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    token_address TEXT NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,
    amount_sol REAL NOT NULL,
    amount_tokens REAL,
    price REAL NOT NULL,
    fee REAL DEFAULT 0,
    slippage REAL DEFAULT 0,
    tx_signature TEXT,
    mode TEXT DEFAULT 'paper',
    status TEXT DEFAULT 'completed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. signals: Trading signals
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    token_address TEXT NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,
    score REAL NOT NULL,
    uncertainty REAL DEFAULT 1.0,
    factors JSONB,
    reasons TEXT,
    sent_to_telegram BOOLEAN DEFAULT FALSE,
    telegram_message_id TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. daily_reports: Daily summary reports
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

-- 8. llm_logs: LLM API call logs
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

-- 9. settings: System settings
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tokens_updated ON tokens (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_ohlcv_address ON ohlcv (address);
CREATE INDEX IF NOT EXISTS idx_ohlcv_time ON ohlcv (time DESC);
CREATE INDEX IF NOT EXISTS idx_strategies_status ON strategies (status);
CREATE INDEX IF NOT EXISTS idx_strategies_score ON strategies (score DESC);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions (status);
CREATE INDEX IF NOT EXISTS idx_trades_created ON trades (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_created ON signals (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports (date);

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

SELECT 'AlphaGPT database schema initialized successfully!' as status;
