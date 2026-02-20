-- AlphaGPT 数据库初始化脚本
-- 在 Supabase SQL Editor 中运行此脚本

-- 1. 创建 tokens 表
CREATE TABLE IF NOT EXISTS tokens (
    address TEXT PRIMARY KEY,
    symbol TEXT,
    name TEXT,
    decimals INT,
    chain TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- 2. 创建 ohlcv 表（K线数据）
CREATE TABLE IF NOT EXISTS ohlcv (
    time TIMESTAMP NOT NULL,
    address TEXT NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    liquidity DOUBLE PRECISION,
    fdv DOUBLE PRECISION,
    source TEXT,
    PRIMARY KEY (time, address)
);

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_ohlcv_address ON ohlcv (address);
CREATE INDEX IF NOT EXISTS idx_ohlcv_time ON ohlcv (time DESC);
CREATE INDEX IF NOT EXISTS idx_tokens_updated ON tokens (last_updated DESC);

-- 4. 创建策略表
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    name TEXT,
    formula JSONB,
    score DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. 创建持仓记录表
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    token_address TEXT,
    symbol TEXT,
    entry_price DOUBLE PRECISION,
    entry_time TIMESTAMP DEFAULT NOW(),
    amount_sol DOUBLE PRECISION,
    amount_tokens DOUBLE PRECISION,
    status TEXT DEFAULT 'open',
    exit_price DOUBLE PRECISION,
    exit_time TIMESTAMP,
    pnl DOUBLE PRECISION
);

-- 6. 创建交易日志表
CREATE TABLE IF NOT EXISTS trade_logs (
    id SERIAL PRIMARY KEY,
    token_address TEXT,
    action TEXT,
    amount DOUBLE PRECISION,
    price DOUBLE PRECISION,
    tx_signature TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. 创建信号记录表
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    token_address TEXT,
    symbol TEXT,
    score DOUBLE PRECISION,
    factors JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. 启用 Row Level Security（可选）
-- ALTER TABLE tokens ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ohlcv ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE trade_logs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE signals ENABLE ROW LEVEL SECURITY;

-- 9. 创建公开访问策略（如果使用 RLS）
-- CREATE POLICY "Allow all for anon" ON tokens FOR ALL TO anon USING (true);
-- CREATE POLICY "Allow all for anon" ON ohlcv FOR ALL TO anon USING (true);

-- 完成
SELECT 'AlphaGPT database initialized successfully!' as status;
