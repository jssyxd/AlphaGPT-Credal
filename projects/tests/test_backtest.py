"""
Tests for backtest module
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
from datetime import datetime, timedelta


def test_backtester_init():
    """Test Backtester initialization"""
    from backtest.backtester import Backtester

    bt = Backtester(initial_capital=5000)
    assert bt.initial_capital == 5000
    assert bt.capital == 5000


def test_backtester_empty_data():
    """Test backtest with empty data"""
    from backtest.backtester import Backtester

    bt = Backtester()
    data = pd.DataFrame()
    strategy = {'formula': 'volume * liquidity > 10000'}

    result = bt.run_backtest(data, strategy)

    assert result['total_trades'] == 0


def test_backtester_basic_data():
    """Test backtest with basic data"""
    from backtest.backtester import Backtester

    # Create sample data
    dates = [datetime.now() - timedelta(hours=i) for i in range(10)]
    data = pd.DataFrame({
        'time': dates,
        'open': [100] * 10,
        'high': [105] * 10,
        'low': [95] * 10,
        'close': [100, 102, 104, 103, 105, 107, 106, 108, 110, 109],
        'volume': [100000] * 10,
        'liquidity': [1000] * 10,
        'price_change_24h': [5] * 10
    })
    data = data.sort_values('time').reset_index(drop=True)

    strategy = {'formula': 'volume * liquidity > 50000'}
    bt = Backtester(initial_capital=1000)

    result = bt.run_backtest(data, strategy, {'position_size_pct': 0.1, 'stop_loss_pct': 0.05, 'take_profit_pct': 0.10})

    assert 'total_trades' in result
    assert 'win_rate' in result


def test_strategy_score():
    """Test strategy scoring"""
    from backtest.backtester import Backtester

    bt = Backtester()

    result = {
        'win_rate': 60,
        'sharpe_ratio': 1.5,
        'max_drawdown': 10
    }

    score = bt._strategy_score(result)
    assert score > 0


def test_generate_variations():
    """Test strategy variation generation"""
    from backtest.backtester import RewardIterator, Backtester

    bt = Backtester()
    ri = RewardIterator(bt)

    base_strategy = {'formula': 'volume * liquidity > 10000', 'name': 'base'}

    variations = ri.generate_variations(base_strategy, count=3)

    assert len(variations) == 3
    for v in variations:
        assert 'formula' in v
        assert 'name' in v


def test_walk_forward_optimize():
    """Test walk-forward optimization"""
    from backtest.backtester import Backtester

    dates = [datetime.now() - timedelta(hours=i) for i in range(50)]
    data = pd.DataFrame({
        'time': dates,
        'close': [100 + i for i in range(50)],
        'volume': [100000] * 50,
        'liquidity': [1000] * 50,
        'price_change_24h': [5] * 50
    })

    strategies = [
        {'formula': 'volume * liquidity > 50000', 'name': 's1'},
        {'formula': 'price_change > 5', 'name': 's2'}
    ]

    bt = Backtester()
    results = bt.walk_forward_optimize(data, strategies, train_window=20, test_window=10)

    assert isinstance(results, list)
