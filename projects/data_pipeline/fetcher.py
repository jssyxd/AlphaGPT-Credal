"""
AlphaGPT Data Pipeline - Data Fetchers
Fetches data from Birdeye and DexScreener APIs
"""
import os
import aiohttp
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()


class BaseFetcher:
    """Base class for data fetchers"""

    def __init__(self):
        self.api_key = os.getenv("BIRDEYE_API_KEY")
        self.base_url = "https://api.birdeye.so"
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class BirdEyeFetcher(BaseFetcher):
    """BirdEye API data fetcher"""

    async def get_token_data(self, address: str) -> Dict:
        """Get token data from BirdEye"""
        session = await self._get_session()
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        url = f"{self.base_url}/defi/token/{address}"
        params = {"chain": "solana"}

        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
                return {}
        except Exception:
            return {}

    async def get_token_list(self, sort_by: str = "liquidity", limit: int = 50) -> List[Dict]:
        """Get list of tokens"""
        session = await self._get_session()
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        url = f"{self.base_url}/defi/tokenlist"
        params = {
            "chain": "solana",
            "sortby": sort_by,
            "limit": limit,
            "type": "meme"
        }

        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {}).get("tokens", [])
                return []
        except Exception:
            return []

    async def get_token_ohlcv(self, address: str, timeframe: str = "1H") -> List[Dict]:
        """Get OHLCV data"""
        session = await self._get_session()
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        from datetime import datetime, timedelta
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=7)).timestamp())

        url = f"{self.base_url}/defi/history/token/{address}"
        params = {
            "chain": "solana",
            "type": timeframe,
            "time_from": start_time,
            "time_to": end_time
        }

        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {}).get("items", [])
                return []
        except Exception:
            return []


class DexScreenerFetcher(BaseFetcher):
    """DexScreener API data fetcher"""

    async def get_token_data(self, address: str) -> Dict:
        """Get token data from DexScreener"""
        session = await self._get_session()

        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("pair", {})
                return {}
        except Exception:
            return {}

    async def get_token_pairs(self, address: str) -> List[Dict]:
        """Get all trading pairs for a token"""
        session = await self._get_session()

        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("pairs", [])
                return []
        except Exception:
            return []


# Convenience functions
async def fetch_meme_tokens(limit: int = 50) -> List[Dict]:
    """Fetch top meme tokens from Birdeye"""
    async with BirdEyeFetcher() as fetcher:
        tokens = await fetcher.get_token_list(sort_by="liquidity", limit=limit)
        return tokens


async def fetch_token_details(address: str) -> Dict:
    """Get token details from multiple sources"""
    async with BirdEyeFetcher() as birdeye, DexScreenerFetcher() as dexscreener:
        b_data = await birdeye.get_token_data(address)
        d_data = await dexscreener.get_token_data(address)

        return {
            "address": address,
            "birdeye": b_data,
            "dexscreener": d_data
        }
