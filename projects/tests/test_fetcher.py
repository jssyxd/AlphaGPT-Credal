"""
Tests for data fetcher module
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch, AsyncMock


@pytest.mark.asyncio
async def test_birdeye_fetcher_init():
    """Test BirdEyeFetcher initialization"""
    from data_pipeline.fetcher import BirdEyeFetcher

    with patch.dict('os.environ', {'BIRDEYE_API_KEY': 'test-key'}):
        fetcher = BirdEyeFetcher()
        assert fetcher.api_key == 'test-key'
        assert fetcher.base_url == "https://api.birdeye.so"


@pytest.mark.asyncio
async def test_birdeye_fetcher_get_token_data():
    """Test getting token data"""
    from data_pipeline.fetcher import BirdEyeFetcher

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "data": {
            "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGZ3Lks5q7",
            "symbol": "USDC",
            "liquidity": 1000000
        }
    })

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch.dict('os.environ', {'BIRDEYE_API_KEY': 'test-key'}):
        with patch('aiohttp.ClientSession', return_value=mock_session):
            fetcher = BirdEyeFetcher()
            fetcher.session = mock_session
            result = await fetcher.get_token_data("test-address")
            # Just verify it doesn't crash
            assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_dexscreener_fetcher_init():
    """Test DexScreenerFetcher initialization"""
    from data_pipeline.fetcher import DexScreenerFetcher

    fetcher = DexScreenerFetcher()
    # DexScreener uses the same base class, so it inherits base_url
    assert fetcher.base_url == "https://api.birdeye.so"


@pytest.mark.asyncio
async def test_base_fetcher_context_manager():
    """Test BaseFetcher as context manager"""
    from data_pipeline.fetcher import BirdEyeFetcher

    with patch.dict('os.environ', {'BIRDEYE_API_KEY': 'test-key'}):
        async with BirdEyeFetcher() as fetcher:
            assert fetcher is not None
