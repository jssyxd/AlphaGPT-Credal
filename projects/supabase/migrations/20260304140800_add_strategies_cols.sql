-- Add missing columns to strategies table

ALTER TABLE strategies ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS formula_json JSONB;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS uncertainty REAL DEFAULT 1.0;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS backtest_result JSONB;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS performance_metrics JSONB;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Add missing columns to signals table
ALTER TABLE signals ADD COLUMN IF NOT EXISTS action TEXT;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS uncertainty REAL DEFAULT 1.0;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS reasons TEXT;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS sent_to_telegram BOOLEAN DEFAULT FALSE;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS telegram_message_id TEXT;

-- Add missing columns to positions table
ALTER TABLE positions ADD COLUMN IF NOT EXISTS pnl_percent REAL;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS stop_loss_price REAL;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS take_profit_price REAL;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE positions ADD COLUMN IF NOT EXISTS decimals INT DEFAULT 9;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS chain TEXT DEFAULT 'solana';

-- Add missing columns to trade_logs table
ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS symbol TEXT;
ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS amount_sol REAL;
ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS amount_tokens REAL;
ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS fee REAL DEFAULT 0;
ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS slippage REAL DEFAULT 0;
ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS mode TEXT DEFAULT 'paper';
ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'completed';
ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS notes TEXT;
