import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase 配置
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # 数据库直连配置（Supabase Postgres）
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    
    # 构建 DSN（支持 Supabase）
    DB_DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # 链配置
    CHAIN = "solana"
    TIMEFRAME = "1m"
    
    # 流动性过滤
    MIN_LIQUIDITY_USD = 50000.0  # 降低门槛，适合小资金
    MIN_FDV = 1000000.0          # 降低门槛
    MAX_FDV = float('inf')
    
    # Birdeye API
    BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "")
    BIRDEYE_IS_PAID = False
    USE_DEXSCREENER = True
    
    # 并发配置
    CONCURRENCY = 10
    HISTORY_DAYS = 3
    
    # 运行模式
    MODE = os.getenv("MODE", "paper")
