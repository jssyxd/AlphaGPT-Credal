import asyncpg
from loguru import logger
from .config import Config

class DBManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                dsn=Config.DB_DSN,
                ssl='require'  # Supabase 需要 SSL
            )
            logger.info("Database connection established.")

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def init_schema(self):
        async with self.pool.acquire() as conn:
            # 创建 tokens 表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    address TEXT PRIMARY KEY,
                    symbol TEXT,
                    name TEXT,
                    decimals INT,
                    chain TEXT,
                    last_updated TIMESTAMP DEFAULT NOW()
                );
            """)

            # 创建 ohlcv 表（K线数据）
            await conn.execute("""
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
            """)
            
            # 尝试创建 TimescaleDB 超级表（如果可用）
            try:
                await conn.execute("SELECT create_hypertable('ohlcv', 'time', if_not_exists => TRUE);")
                logger.info("Converted ohlcv to Hypertable.")
            except Exception:
                logger.warning("TimescaleDB extension not found, using standard Postgres.")

            # 创建索引
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_ohlcv_address ON ohlcv (address);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_ohlcv_time ON ohlcv (time DESC);")

    async def upsert_tokens(self, tokens):
        if not tokens: return
        async with self.pool.acquire() as conn:
            await conn.executemany("""
                INSERT INTO tokens (address, symbol, name, decimals, chain, last_updated)
                VALUES ($1, $2, $3, $4, $5, NOW())
                ON CONFLICT (address) DO UPDATE 
                SET symbol = EXCLUDED.symbol, last_updated = NOW();
            """, tokens)

    async def batch_insert_ohlcv(self, records):
        if not records: return
        async with self.pool.acquire() as conn:
            try:
                await conn.copy_records_to_table(
                    'ohlcv',
                    records=records,
                    columns=['time', 'address', 'open', 'high', 'low', 'close', 
                             'volume', 'liquidity', 'fdv', 'source'],
                    timeout=60
                )
            except asyncpg.UniqueViolationError:
                pass
            except Exception as e:
                logger.error(f"Batch insert error: {e}")

    async def get_latest_tokens(self, limit=100):
        """获取最新的代币列表"""
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT address, symbol, name FROM tokens 
                ORDER BY last_updated DESC 
                LIMIT $1
            """, limit)

    async def get_ohlcv_for_token(self, address, hours=24):
        """获取指定代币的K线数据"""
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT * FROM ohlcv 
                WHERE address = $1 
                AND time > NOW() - INTERVAL '%s hours'
                ORDER BY time ASC
            """ % hours, address)
