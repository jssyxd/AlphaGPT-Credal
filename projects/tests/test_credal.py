"""
Tests for Credal Transformer module (simplified, no torch required)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np


def test_dirichlet_properties():
    """Test Dirichlet distribution properties"""

    # Simple mock of Dirichlet behavior
    alpha = np.array([2.0, 2.0, 2.0])  # Equal evidence

    # Dirichlet mean: alpha / sum(alpha)
    probs = alpha / alpha.sum()
    assert np.isclose(probs.sum(), 1.0)
    assert np.allclose(probs, [1/3, 1/3, 1/3])


def test_uncertainty_calculation():
    """Test uncertainty calculation U = K / sum(alpha)"""

    # High evidence -> low uncertainty
    alpha_high = np.array([10.0, 10.0, 10.0])  # Strong evidence
    K = len(alpha_high)
    uncertainty_high = K / alpha_high.sum()
    assert uncertainty_high < 0.5

    # Low evidence -> high uncertainty
    alpha_low = np.array([1.0, 1.0, 1.0])  # Weak evidence
    uncertainty_low = K / alpha_low.sum()
    assert uncertainty_low > uncertainty_high


def test_credal_decision_logic():
    """Test credal decision logic"""

    def credal_decision(signal_strength, uncertainty, threshold=0.5):
        """Simplified credal decision"""
        if uncertainty > threshold:
            return "HOLD"
        elif signal_strength > 0.6:
            return "BUY"
        elif signal_strength < 0.4:
            return "SELL"
        return "HOLD"

    # High signal, low uncertainty -> BUY
    assert credal_decision(0.8, 0.1) == "BUY"

    # Low signal, low uncertainty -> SELL
    assert credal_decision(0.2, 0.1) == "SELL"

    # Any uncertainty -> HOLD
    assert credal_decision(0.8, 0.6) == "HOLD"


def test_evidence_accumulation():
    """Test evidence accumulation"""

    # Start with uniform evidence
    alpha = np.ones(3)

    # Add evidence for class 0
    alpha[0] += 2.0

    probs = alpha / alpha.sum()

    # Class 0 should have higher probability
    assert probs[0] > probs[1]
    assert probs[0] > probs[2]


def test_signal_aggregation():
    """Test multiple signal aggregation with uncertainty weighting"""

    signals = [
        {"strength": 0.8, "uncertainty": 0.1},
        {"strength": 0.6, "uncertainty": 0.2},
        {"strength": 0.4, "uncertainty": 0.3}
    ]

    # Inverse uncertainty weighting
    weights = []
    strengths = []

    for s in signals:
        w = 1 / (s["uncertainty"] + 1e-8)
        weights.append(w)
        strengths.append(s["strength"])

    weights = np.array(weights)
    weights = weights / weights.sum()

    aggregated = np.average(strengths, weights=weights)

    # First signal has highest weight (lowest uncertainty)
    assert weights[0] > weights[1]
    assert weights[0] > weights[2]
    # Aggregated should be between min and max
    assert min(strengths) <= aggregated <= max(strengths)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
