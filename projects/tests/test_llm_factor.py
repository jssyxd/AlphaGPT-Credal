"""
Tests for LLM factor generator module
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch


def test_llm_generator_init():
    """Test LLMFactorGenerator initialization"""
    from model_core.llm_factor_generator import LLMFactorGenerator

    with patch.dict('os.environ', {
        'MIMO_API_URL': 'https://api.test.com',
        'MIMO_API_KEY': 'test-key',
        'MIMO_MODEL': 'test-model'
    }):
        gen = LLMFactorGenerator()
        assert gen.api_url == 'https://api.test.com'
        assert gen.api_key == 'test-key'
        assert gen.model == 'test-model'


def test_generate_factor_no_api_key():
    """Test generate_factor returns mock when no API key"""
    from model_core.llm_factor_generator import LLMFactorGenerator

    # Clear API key
    with patch.dict('os.environ', {'MIMO_API_KEY': ''}, clear=True):
        gen = LLMFactorGenerator()
        result = gen.generate_factor(["SOL", "BONK"])

        assert "formula" in result
        assert result["model"] == "mock"
        assert result["score"] == 0.75


def test_generate_multiple_factors():
    """Test generate_multiple_factors"""
    from model_core.llm_factor_generator import LLMFactorGenerator

    with patch.dict('os.environ', {'MIMO_API_KEY': ''}, clear=True):
        gen = LLMFactorGenerator()
        factors = gen.generate_multiple_factors(["SOL", "BONK"], count=3)

        assert len(factors) == 3
        for i, factor in enumerate(factors):
            assert "formula" in factor
            assert factor["name"] == f"factor_{i+1}"


def test_get_llm_generator_singleton():
    """Test get_llm_generator returns singleton"""
    from model_core.llm_factor_generator import get_llm_generator, LLMFactorGenerator

    # Reset singleton
    import model_core.llm_factor_generator as module
    module._generator = None

    with patch.dict('os.environ', {'MIMO_API_KEY': ''}, clear=True):
        gen1 = get_llm_generator()
        gen2 = get_llm_generator()

        assert gen1 is gen2
        assert isinstance(gen1, LLMFactorGenerator)
