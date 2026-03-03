"""
AlphaGPT Backtest Module
Enhanced backtesting with walk-forward optimization and reward iteration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json


class Backtester:
    """Enhanced backtesting engine with reward iteration"""

    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []

    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy: Dict,
        config: Dict = None
    ) -> Dict:
        """Run backtest on historical data"""
        config = config or {}

        position_size_pct = config.get('position_size_pct', 0.1)
        stop_loss_pct = config.get('stop_loss_pct', 0.05)
        take_profit_pct = config.get('take_profit_pct', 0.10)

        self.capital = self.initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = [self.capital]

        formula = strategy.get('formula', '')

        for i in range(1, len(data)):
            row = data.iloc[i]
            prev_row = data.iloc[i-1]

            # Generate signal
            signal = self._evaluate_signal(prev_row, formula)

            current_price = row.get('close', 0)
            if current_price <= 0:
                continue

            # Check existing positions for exit
            self._check_exits(
                row,
                current_price,
                stop_loss_pct,
                take_profit_pct
            )

            # Entry signal
            if signal == 'BUY' and len(self.positions) < config.get('max_positions', 3):
                position_value = self.capital * position_size_pct
                tokens = position_value / current_price

                self.positions.append({
                    'entry_price': current_price,
                    'entry_time': row.get('time', datetime.now()),
                    'tokens': tokens,
                    'value': position_value
                })
                self.capital -= position_value

            # Record equity
            self.equity_curve.append(self.capital + sum(p['tokens'] * current_price for p in self.positions))

        return self._calculate_metrics()

    def _evaluate_signal(self, data: pd.Series, formula: str) -> Optional[str]:
        """Evaluate trading signal from formula"""
        try:
            # Map formula variables to data
            volume = data.get('volume', 0)
            liquidity = data.get('liquidity', 0)
            price_change = data.get('price_change_24h', 0)
            holders = data.get('holders', 0)

            # Simple evaluation
            if 'volume * liquidity' in formula:
                if volume * liquidity > 50000:
                    return 'BUY'
            if 'price_change' in formula and '>' in formula:
                if price_change > 5:
                    return 'BUY'

            return None
        except:
            return None

    def _check_exits(
        self,
        row: pd.Series,
        current_price: float,
        stop_loss_pct: float,
        take_profit_pct: float
    ):
        """Check and execute position exits"""
        exits = []

        for i, pos in enumerate(self.positions):
            pnl_pct = (current_price - pos['entry_price']) / pos['entry_price']

            if pnl_pct <= -stop_loss_pct:
                exits.append((i, 'stop_loss', pnl_pct))
            elif pnl_pct >= take_profit_pct:
                exits.append((i, 'take_profit', pnl_pct))

        # Execute exits in reverse order
        for i, reason, pnl_pct in reversed(exits):
            pos = self.positions.pop(i)
            exit_value = pos['tokens'] * current_price
            pnl = exit_value - pos['value']

            self.trades.append({
                'entry_price': pos['entry_price'],
                'exit_price': current_price,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'exit_reason': reason,
                'entry_time': pos['entry_time'],
                'exit_time': row.get('time', datetime.now())
            })
            self.capital += exit_value

    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'total_return': 0
            }

        winning = [t for t in self.trades if t['pnl'] > 0]
        losing = [t for t in self.trades if t['pnl'] <= 0]

        returns = [t['pnl_pct'] for t in self.trades]

        # Sharpe ratio
        if np.std(returns) > 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
        else:
            sharpe = 0

        # Max drawdown
        equity = np.array(self.equity_curve)
        peak = np.maximum.accumulate(equity)
        drawdown = (peak - equity) / peak
        max_dd = np.max(drawdown) * 100

        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': len(winning) / len(self.trades) * 100 if self.trades else 0,
            'total_return': (self.capital - self.initial_capital) / self.initial_capital * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'avg_win': np.mean([t['pnl_pct'] for t in winning]) if winning else 0,
            'avg_loss': np.mean([t['pnl_pct'] for t in losing]) if losing else 0,
            'profit_factor': abs(sum(t['pnl'] for t in winning) / sum(t['pnl'] for t in losing)) if losing and sum(t['pnl'] for t in losing) != 0 else 0
        }

    def walk_forward_optimize(
        self,
        data: pd.DataFrame,
        strategies: List[Dict],
        train_window: int = 30,
        test_window: int = 7
    ) -> List[Dict]:
        """Walk-forward optimization"""
        results = []

        for i in range(train_window, len(data) - test_window, test_window):
            train_data = data.iloc[i-train_window:i]
            test_data = data.iloc[i:i+test_window]

            # Find best strategy on training data
            best_strategy = None
            best_score = -float('inf')

            for strategy in strategies:
                result = self.run_backtest(train_data, strategy)
                score = self._strategy_score(result)

                if score > best_score:
                    best_score = score
                    best_strategy = strategy

            # Test on validation data
            if best_strategy:
                test_result = self.run_backtest(test_data, best_strategy)
                results.append({
                    'train_result': best_score,
                    'test_result': test_result,
                    'strategy': best_strategy,
                    'period': (i, i + test_window)
                })

        return results

    def _strategy_score(self, result: Dict) -> float:
        """Calculate strategy score for optimization"""
        win_rate = result.get('win_rate', 0)
        sharpe = result.get('sharpe_ratio', 0)
        max_dd = result.get('max_drawdown', 100)

        # Weighted score
        return win_rate * 0.3 + sharpe * 40 - max_dd * 0.5


class RewardIterator:
    """Reward iteration for strategy improvement"""

    def __init__(self, backtester: Backtester):
        self.backtester = backtester
        self.best_strategies = []
        self.generation = 0

    def generate_variations(self, base_strategy: Dict, count: int = 5) -> List[Dict]:
        """Generate strategy variations"""
        variations = []
        formula = base_strategy.get('formula', '')

        # Mutation operators
        operators = ['>', '<', '>=', '<=']
        thresholds = [10000, 20000, 50000, 100000]

        for i in range(count):
            new_formula = formula

            # Random mutation
            if i % 3 == 0:
                # Change threshold
                for th in thresholds:
                    if str(th) in formula:
                        new_formula = formula.replace(str(th), str(th * 1.5))
                        break
            elif i % 3 == 1:
                # Change operator
                for op in operators:
                    if op in formula:
                        new_formula = formula.replace(op, operators[(operators.index(op) + 1) % len(operators)])
                        break

            variations.append({
                'formula': new_formula,
                'name': f"gen_{self.generation}_variant_{i}",
                'parent': base_strategy.get('name')
            })

        return variations

    def evolve(
        self,
        data: pd.DataFrame,
        population: List[Dict],
        generations: int = 5,
        elite_count: int = 2
    ) -> Dict:
        """Evolve strategies through reward iteration"""

        for gen in range(generations):
            self.generation = gen

            # Evaluate all strategies
            results = []
            for strategy in population:
                result = self.backtester.run_backtest(data, strategy)
                score = self.backtester._strategy_score(result)
                results.append((strategy, result, score))

            # Sort by score
            results.sort(key=lambda x: x[2], reverse=True)

            # Keep elite
            elite = results[:elite_count]
            self.best_strategies.extend([r[0] for r in elite])

            # Generate new population
            new_population = [r[0] for r in elite]

            while len(new_population) < len(population):
                parent = results[np.random.randint(0, len(results) // 2)][0]
                variations = self.generate_variations(parent)
                new_population.extend(variations[:2])

            population = new_population[:len(population)]

        # Return best strategy
        return self.best_strategies[0] if self.best_strategies else population[0]


def run_backtest(data: pd.DataFrame, strategy: Dict, config: Dict = None) -> Dict:
    """Convenience function to run backtest"""
    backtester = Backtester()
    return backtester.run_backtest(data, strategy, config)
