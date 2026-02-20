"""
回测引擎 - 严格的历史验证框架
支持80/20样本外验证、夏普比率计算、日本税务合规
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from scipy import stats


@dataclass
class BacktestConfig:
    """回测配置"""
    initial_capital: float = 1000.0  # 初始资金（低资金设置）
    position_size_pct: float = 0.01  # 每笔交易1%风险
    stop_loss_pct: float = 0.05  # 止损5%
    take_profit_pct: float = 0.10  # 止盈10%
    trailing_stop_pct: float = 0.05  # 移动止盈5%
    max_positions: int = 5  # 最大持仓数
    commission_rate: float = 0.001  # 手续费0.1%（Solana很低）
    slippage_pct: float = 0.001  # 滑点0.1%
    train_ratio: float = 0.8  # 80%训练，20%测试
    min_liquidity_usd: float = 10000.0  # 最低流动性$10k


@dataclass
class Trade:
    """交易记录"""
    entry_time: datetime
    exit_time: Optional[datetime]
    token: str
    entry_price: float
    exit_price: Optional[float]
    position_size: float
    action: str  # 'buy', 'sell'
    pnl: float = 0.0
    pnl_pct: float = 0.0
    exit_reason: str = ''
    holding_periods: int = 0


@dataclass
class BacktestResult:
    """回测结果"""
    total_return: float
    sharpe_ratio: float
    win_rate: float
    max_drawdown: float
    profit_factor: float
    num_trades: int
    avg_trade: float
    avg_win: float
    avg_loss: float
    trades: List[Trade]
    equity_curve: pd.Series
    japan_tax_info: Dict


class BacktestEngine:
    """
    回测引擎
    实现严格的历史验证和风险控制
    """

    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.current_positions: Dict[str, Trade] = {}
        self.cash: float = self.config.initial_capital
        self.total_equity: float = self.config.initial_capital

    def run_walk_forward(
        self,
        data: pd.DataFrame,
        strategy_fn,
        n_splits: int = 5
    ) -> List[BacktestResult]:
        """
        Walk-forward优化
        滚动训练/测试窗口防止过拟合

        Args:
            data: 历史数据DataFrame
            strategy_fn: 策略函数
            n_splits: 分割数量

        Returns:
            每个窗口的回测结果列表
        """
        results = []
        data_length = len(data)
        window_size = data_length // n_splits

        for i in range(n_splits - 1):
            # 训练窗口
            train_start = i * window_size
            train_end = (i + 1) * window_size
            # 测试窗口
            test_start = train_end
            test_end = min((i + 2) * window_size, data_length)

            train_data = data.iloc[train_start:train_end]
            test_data = data.iloc[test_start:test_end]

            # 在训练数据上优化策略参数
            optimized_params = self._optimize_params(train_data, strategy_fn)

            # 在测试数据上运行回测
            result = self.run_backtest(test_data, strategy_fn, optimized_params)
            results.append(result)

            print(f"Window {i+1}: Train {train_start}-{train_end}, Test {test_start}-{test_end}")
            print(f"  Return: {result.total_return:.2%}, Sharpe: {result.sharpe_ratio:.2f}, Win Rate: {result.win_rate:.2%}")

        return results

    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy_fn,
        params: Optional[Dict] = None
    ) -> BacktestResult:
        """
        运行回测

        Args:
            data: 历史数据，包含price, volume, liquidity等列
            strategy_fn: 策略函数，返回交易信号
            params: 策略参数

        Returns:
            BacktestResult对象
        """
        self.reset()

        for i in range(len(data)):
            current_bar = data.iloc[i]
            current_time = data.index[i] if isinstance(data.index[i], datetime) else datetime.now()

            # 获取策略信号
            signal = strategy_fn(data.iloc[:i+1], params)

            # 更新持仓
            self._update_positions(current_bar, current_time)

            # 执行信号
            if signal == 'buy' and len(self.current_positions) < self.config.max_positions:
                self._open_position(current_bar, current_time)
            elif signal == 'sell' and self.current_positions:
                self._close_all_positions(current_bar, current_time, 'signal')

            # 记录权益曲线
            self._update_equity(current_bar)

        # 关闭所有剩余持仓
        if self.current_positions:
            self._close_all_positions(data.iloc[-1], data.index[-1], 'end_of_data')

        return self._calculate_metrics()

    def run_oos_validation(
        self,
        train_data: pd.DataFrame,
        test_data: pd.DataFrame,
        strategy_fn
    ) -> Tuple[BacktestResult, BacktestResult]:
        """
        80/20 样本外验证

        Returns:
            (训练集结果, 测试集结果)
        """
        # 在训练集上优化参数
        train_params = self._optimize_params(train_data, strategy_fn)

        # 训练集结果
        train_result = self.run_backtest(train_data, strategy_fn, train_params)

        # 测试集结果（使用训练集优化的参数）
        test_result = self.run_backtest(test_data, strategy_fn, train_params)

        # 检查过拟合
        overfit_ratio = train_result.sharpe_ratio / max(test_result.sharpe_ratio, 0.01)

        print("\n=== OOS Validation Results ===")
        print(f"Train: Return={train_result.total_return:.2%}, Sharpe={train_result.sharpe_ratio:.2f}")
        print(f"Test:  Return={test_result.total_return:.2%}, Sharpe={test_result.sharpe_ratio:.2f}")
        print(f"Overfit Ratio: {overfit_ratio:.2f} (>1.5 indicates overfitting)")

        if overfit_ratio > 1.5:
            print("WARNING: Strategy may be overfitted to training data!")

        return train_result, test_result

    def _open_position(self, bar: pd.Series, time: datetime):
        """开仓"""
        # 流动性检查
        if bar.get('liquidity', float('inf')) < self.config.min_liquidity_usd:
            return

        # 计算仓位大小（1%风险）
        position_value = self.total_equity * self.config.position_size_pct

        # 考虑手续费和滑点
        entry_price = bar['close'] * (1 + self.config.slippage_pct)

        trade = Trade(
            entry_time=time,
            exit_time=None,
            token=bar.get('address', 'unknown'),
            entry_price=entry_price,
            exit_price=None,
            position_size=position_value / entry_price,
            action='buy'
        )

        self.current_positions[bar.get('address', 'unknown')] = trade
        self.cash -= position_value * (1 + self.config.commission_rate)

    def _update_positions(self, bar: pd.Series, time: datetime):
        """更新持仓状态，检查止损止盈"""
        for token, trade in list(self.current_positions.items()):
            current_price = bar['close']
            trade.holding_periods += 1

            # 计算未实现盈亏
            unrealized_pct = (current_price - trade.entry_price) / trade.entry_price

            # 检查止损
            if unrealized_pct <= -self.config.stop_loss_pct:
                self._close_position(token, bar, time, 'stop_loss')

            # 检查止盈
            elif unrealized_pct >= self.config.take_profit_pct:
                self._close_position(token, bar, time, 'take_profit')

            # 检查移动止盈
            elif trade.holding_periods > 10:  # 持仓超过10个周期后启用
                # 简化版：从高点回落5%
                high_since_entry = bar.get('high', current_price)
                if high_since_entry > trade.entry_price * 1.05:  # 已盈利5%以上
                    drawdown_from_high = (high_since_entry - current_price) / high_since_entry
                    if drawdown_from_high >= self.config.trailing_stop_pct:
                        self._close_position(token, bar, time, 'trailing_stop')

    def _close_position(self, token: str, bar: pd.Series, time: datetime, reason: str):
        """平仓单个持仓"""
        if token not in self.current_positions:
            return

        trade = self.current_positions[token]
        trade.exit_time = time

        # 考虑滑点和手续费
        exit_price = bar['close'] * (1 - self.config.slippage_pct)
        trade.exit_price = exit_price

        # 计算盈亏
        trade.pnl = (exit_price - trade.entry_price) * trade.position_size
        trade.pnl_pct = (exit_price - trade.entry_price) / trade.entry_price
        trade.exit_reason = reason

        # 更新现金
        position_value = trade.position_size * exit_price
        self.cash += position_value * (1 - self.config.commission_rate)

        # 记录交易
        self.trades.append(trade)
        del self.current_positions[token]

    def _close_all_positions(self, bar: pd.Series, time: datetime, reason: str):
        """平仓所有持仓"""
        for token in list(self.current_positions.keys()):
            self._close_position(token, bar, time, reason)

    def _update_equity(self, bar: pd.Series):
        """更新权益曲线"""
        unrealized_pnl = 0
        for trade in self.current_positions.values():
            current_price = bar['close']
            unrealized_pnl += (current_price - trade.entry_price) * trade.position_size

        self.total_equity = self.cash + unrealized_pnl
        self.equity_curve.append(self.total_equity)

    def _optimize_params(self, data: pd.DataFrame, strategy_fn) -> Dict:
        """简单参数优化（网格搜索）"""
        # 简化版：返回默认参数
        return {'threshold': 0.5}

    def _calculate_metrics(self) -> BacktestResult:
        """计算回测指标"""
        equity_series = pd.Series(self.equity_curve)

        # 总收益
        total_return = (self.total_equity - self.config.initial_capital) / self.config.initial_capital

        # 日收益率
        if len(equity_series) > 1:
            daily_returns = equity_series.pct_change().dropna()
        else:
            daily_returns = pd.Series([0])

        # 夏普比率（假设无风险利率0）
        if daily_returns.std() > 0:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0

        # 胜率
        winning_trades = [t for t in self.trades if t.pnl > 0]
        win_rate = len(winning_trades) / max(len(self.trades), 1)

        # 最大回撤
        cummax = equity_series.cummax()
        drawdown = (equity_series - cummax) / cummax
        max_drawdown = drawdown.min()

        # 盈亏比
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        losing_trades = [t for t in self.trades if t.pnl <= 0]
        avg_loss = np.mean([abs(t.pnl) for t in losing_trades]) if losing_trades else 1
        profit_factor = avg_win * len(winning_trades) / max(avg_loss * len(losing_trades), 1)

        # 日本税务信息
        japan_tax_info = self._calculate_japan_tax()

        return BacktestResult(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            profit_factor=profit_factor,
            num_trades=len(self.trades),
            avg_trade=np.mean([t.pnl for t in self.trades]) if self.trades else 0,
            avg_win=avg_win,
            avg_loss=-avg_loss,
            trades=self.trades,
            equity_curve=equity_series,
            japan_tax_info=japan_tax_info
        )

    def _calculate_japan_tax(self) -> Dict:
        """
        计算日本税务信息
        加密资产在日本属于杂项收入，税率取决于总收入
        """
        total_profit = sum(t.pnl for t in self.trades if t.pnl > 0)

        # 简化版税率计算（实际应根据总收入确定）
        if total_profit <= 0:
            tax_rate = 0
        elif total_profit <= 200000:  # 20万日元以下免税
            tax_rate = 0
        elif total_profit <= 1950000:  # 5% ~ 10%
            tax_rate = 0.05
        elif total_profit <= 3300000:
            tax_rate = 0.10
        elif total_profit <= 6950000:
            tax_rate = 0.20
        elif total_profit <= 9000000:
            tax_rate = 0.23
        elif total_profit <= 18000000:
            tax_rate = 0.33
        elif total_profit <= 40000000:
            tax_rate = 0.40
        else:
            tax_rate = 0.45

        estimated_tax = total_profit * tax_rate

        return {
            'total_profit_jpy': float(total_profit),
            'estimated_tax_rate': float(tax_rate),
            'estimated_tax_jpy': float(estimated_tax),
            'after_tax_profit_jpy': float(total_profit - estimated_tax),
            'note': '这是预估税额，请咨询专业税务师。日本加密货币属于杂项收入。',
            'tax_filing_deadline': '次年3月15日',
            'filing_required': total_profit > 200000
        }

    def reset(self):
        """重置回测状态"""
        self.trades = []
        self.equity_curve = []
        self.current_positions = {}
        self.cash = self.config.initial_capital
        self.total_equity = self.config.initial_capital

    def print_report(self, result: BacktestResult):
        """打印回测报告"""
        print("\n" + "="*50)
        print("          AlphaGPT 回测报告")
        print("="*50)
        print(f"总收益率:      {result.total_return:>10.2%}")
        print(f"夏普比率:      {result.sharpe_ratio:>10.2f}")
        print(f"胜率:          {result.win_rate:>10.2%}")
        print(f"最大回撤:      {result.max_drawdown:>10.2%}")
        print(f"盈亏比:        {result.profit_factor:>10.2f}")
        print(f"交易次数:      {result.num_trades:>10}")
        print(f"平均盈亏:      {result.avg_trade:>10.2f} JPY")
        print(f"平均盈利:      {result.avg_win:>10.2f} JPY")
        print(f"平均亏损:      {result.avg_loss:>10.2f} JPY")
        print("-"*50)
        print("           日本税务信息")
        print("-"*50)
        tax_info = result.japan_tax_info
        print(f"预估利润:      {tax_info['total_profit_jpy']:>10.2f} JPY")
        print(f"预估税率:      {tax_info['estimated_tax_rate']:>10.2%}")
        print(f"预估税额:      {tax_info['estimated_tax_jpy']:>10.2f} JPY")
        print(f"税后利润:      {tax_info['after_tax_profit_jpy']:>10.2f} JPY")
        print(f"需要申报:      {('是' if tax_info['filing_required'] else '否'):>10}")
        print(f"申报截止:      {tax_info['tax_filing_deadline']:>10}")
        print("="*50)


# 使用示例
def example_strategy(data: pd.DataFrame, params: Dict) -> str:
    """
    示例策略：简单的均线交叉
    """
    if len(data) < 20:
        return 'hold'

    # 计算均线
    ma5 = data['close'].rolling(5).mean().iloc[-1]
    ma20 = data['close'].rolling(20).mean().iloc[-1]

    # 简单规则
    if ma5 > ma20 * 1.02:  # 5日线上穿20日线2%
        return 'buy'
    elif ma5 < ma20 * 0.98:  # 5线下穿20日线2%
        return 'sell'

    return 'hold'


if __name__ == "__main__":
    # 创建模拟数据
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=252, freq='D')
    prices = 100 * np.exp(np.cumsum(np.random.randn(252) * 0.02))

    data = pd.DataFrame({
        'open': prices * (1 + np.random.randn(252) * 0.001),
        'high': prices * (1 + abs(np.random.randn(252)) * 0.01),
        'low': prices * (1 - abs(np.random.randn(252)) * 0.01),
        'close': prices,
        'volume': np.random.randint(1000, 10000, 252),
        'liquidity': np.random.randint(50000, 200000, 252),
        'address': ['token1'] * 252
    }, index=dates)

    # 运行回测
    config = BacktestConfig(initial_capital=500)  # 低资金设置
    engine = BacktestEngine(config)

    result = engine.run_backtest(data, example_strategy)
    engine.print_report(result)

    # 运行OOS验证
    train_size = int(len(data) * 0.8)
    train_data = data.iloc[:train_size]
    test_data = data.iloc[train_size:]

    train_result, test_result = engine.run_oos_validation(train_data, test_data, example_strategy)

    print("\n" + "="*50)
    print("策略是否可用:", "✓" if test_result.sharpe_ratio > 1.5 and test_result.win_rate > 0.55 else "✗")
    print("="*50)
