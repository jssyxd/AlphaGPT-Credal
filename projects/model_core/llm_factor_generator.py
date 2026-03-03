"""
AlphaGPT LLM Factor Generator
Generates trading factors using MIMO-V2-Flash LLM
"""
import os
import json
import requests
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class LLMFactorGenerator:
    """Generate trading factors using MIMO-V2-Flash LLM"""

    def __init__(self):
        # Configure for MIMO-V2-Flash API
        self.api_url = os.getenv("MIMO_API_URL", "https://api.minimax.chat/v1/text/chatcompletion_v2")
        self.api_key = os.getenv("MIMO_API_KEY")
        self.model = os.getenv("MIMO_MODEL", "MIMO-V2-Flash")

        # Factor generation prompt template
        self.prompt_template = """You are an expert Solana quantitative trading analyst.
Generate factor formula for trading an interpretable alpha meme coins.

Available metrics:
- volume: trading volume
- liquidity: token liquidity
- price_change: 24h price change
- holders: number of holders
- creator_percent: creator token percentage
- fomo_score: social sentiment score

Generate a factor formula that:
1. Uses mathematical operators (+, -, *, /, >, <, >=, <=)
2. Combines 2-4 metrics
3. Is interpretable and has high alpha potential

Return JSON format:
{{"formula": "metric1 * metric2 > threshold", "score": 0.0-1.0, "uncertainty": 0.0-1.0, "reasons": "why this factor works"}}

Example: {{"formula": "volume * liquidity > 50000", "score": 0.8, "uncertainty": 0.15, "reasons": "high volume with high liquidity indicates strong token"}}

Current market context: {context}

Generate a factor:"""

    def generate_factor(self, top_tokens: List[str], context: str = "") -> Dict:
        """Generate a single factor"""
        if not self.api_key:
            # Return mock factor for testing
            return {
                "formula": "volume * liquidity > 50000",
                "score": 0.75,
                "uncertainty": 0.2,
                "reasons": "high volume with high liquidity",
                "model": "mock"
            }

        prompt = self.prompt_template.format(
            context=f"Top tokens: {', '.join(top_tokens[:5])}" + (f". Context: {context}" if context else "")
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Parse JSON from response
            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content)
            result["model"] = self.model

            return result

        except Exception as e:
            return {
                "formula": "volume * liquidity > 50000",
                "score": 0.5,
                "uncertainty": 0.5,
                "reasons": f"Error generating factor: {str(e)}",
                "model": "error"
            }

    def generate_multiple_factors(self, top_tokens: List[str], count: int = 5, context: str = "") -> List[Dict]:
        """Generate multiple factors"""
        factors = []

        contexts = [
            "Focus on liquidity and volume metrics",
            "Focus on holder distribution and price action",
            "Focus on social sentiment and market cap",
            "Focus on risk-adjusted returns",
            "Focus on momentum indicators"
        ]

        for i in range(count):
            ctx = contexts[i % len(contexts)] if context else ""
            factor = self.generate_factor(top_tokens, ctx)
            factor["name"] = f"factor_{i+1}"
            factors.append(factor)

        return factors

    def evaluate_factor(self, formula: str, market_data: Dict) -> Dict:
        """Evaluate a factor against current market data"""
        # Simple evaluation - can be enhanced with actual backtest
        try:
            return {
                "formula": formula,
                "evaluation_score": 0.7,
                "signal_strength": "medium",
                "timestamp": None
            }
        except Exception as e:
            return {
                "formula": formula,
                "evaluation_score": 0,
                "signal_strength": "none",
                "error": str(e)
            }


# Singleton
_generator = None


def get_llm_generator() -> LLMFactorGenerator:
    """Get LLM factor generator singleton"""
    global _generator
    if _generator is None:
        _generator = LLMFactorGenerator()
    return _generator
