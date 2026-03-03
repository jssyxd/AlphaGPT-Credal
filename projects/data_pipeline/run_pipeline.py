"""
AlphaGPT Data Pipeline - Pipeline Runner
Main pipeline for fetching data and generating factors
"""
import asyncio
import logging
from typing import Dict, List
from dotenv import load_dotenv

from data_pipeline.fetcher import fetch_meme_tokens, BirdEyeFetcher
from data_pipeline.db import get_db_manager
from model_core.llm_factor_generator import get_llm_generator
from data_pipeline.strategy_storage import save_strategy

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_and_store_tokens(limit: int = 50) -> int:
    """Fetch top tokens and store in database"""
    db = get_db_manager()
    supabase = db.supabase

    logger.info(f"Fetching top {limit} tokens...")
    tokens = await fetch_meme_tokens(limit=limit)

    stored_count = 0
    for token in tokens:
        try:
            data = {
                "address": token.get("address"),
                "symbol": token.get("symbol", ""),
                "name": token.get("name", ""),
                "decimals": token.get("decimals", 9),
                "liquidity": token.get("liquidity", 0),
                "holders": token.get("holders", 0),
                "price": token.get("price", 0),
                "price_change_24h": token.get("priceChange24h", 0),
                "fdv": token.get("fdv", 0),
                "updated_at": "now()"
            }

            supabase.table("tokens").upsert(data).execute()
            stored_count += 1
        except Exception as e:
            logger.warning(f"Failed to store token {token.get('address')}: {e}")

    logger.info(f"Stored {stored_count} tokens")
    return stored_count


async def fetch_and_store_ohlcv(address: str) -> int:
    """Fetch OHLCV data for a token"""
    fetcher = BirdEyeFetcher()
    supabase = get_db_manager().supabase

    try:
        ohlcv_data = await fetcher.get_token_ohlcv(address)

        stored_count = 0
        for item in ohlcv_data:
            try:
                data = {
                    "time": item.get("time"),
                    "address": address,
                    "open": item.get("open"),
                    "high": item.get("high"),
                    "low": item.get("low"),
                    "close": item.get("close"),
                    "volume": item.get("volume"),
                    "liquidity": item.get("liquidity"),
                    "fdv": item.get("fdv"),
                    "source": "birdeye"
                }

                supabase.table("ohlcv").upsert(data).execute()
                stored_count += 1
            except Exception as e:
                logger.warning(f"Failed to store OHLCV: {e}")

        return stored_count
    finally:
        await fetcher.close()


def generate_and_store_factors(top_tokens: List[str], count: int = 5) -> int:
    """Generate and store new factors"""
    generator = get_llm_generator()
    factors = generator.generate_multiple_factors(top_tokens, count=count)

    stored_count = 0
    for factor in factors:
        try:
            save_strategy(factor)
            stored_count += 1
        except Exception as e:
            logger.warning(f"Failed to store factor: {e}")

    logger.info(f"Generated and stored {stored_count} factors")
    return stored_count


def run_pipeline():
    """Main pipeline runner"""
    return asyncio.run(run_pipeline_async())


async def run_pipeline_async() -> Dict:
    """Async pipeline runner"""
    logger.info("Starting data pipeline...")

    # Step 1: Fetch and store tokens
    token_count = await fetch_and_store_tokens(limit=50)

    # Step 2: Get top tokens for OHLCV
    db = get_db_manager()
    supabase = db.supabase
    response = supabase.table("tokens").select("address").order("liquidity", desc=True).limit(10).execute()
    top_addresses = [row["address"] for row in response.data]

    # Step 3: Fetch OHLCV for top tokens
    ohlcv_count = 0
    for address in top_addresses:
        try:
            count = await fetch_and_store_ohlcv(address)
            ohlcv_count += count
        except Exception as e:
            logger.warning(f"Failed to fetch OHLCV for {address}: {e}")

    logger.info(f"Pipeline complete: {token_count} tokens, {ohlcv_count} OHLCV records")

    return {
        "tokens": token_count,
        "ohlcv": ohlcv_count
    }


if __name__ == "__main__":
    run_pipeline()
