"""
纸交易模块 - 模拟交易环境
支持MODE=paper安全测试，无需真实资金
"""

import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from loguru import logger
import random


@dataclass
class PaperPosition:
    """纸交易持仓"""
    token_address: str
    symbol: str
    entry_price: float
    entry_time: datetime
    amount_tokens: float
    amount_sol: float
    current_price: float
    highest_price: float
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    is_moonbag: bool = False

    def update_price(self, new_price: float):
        """更新价格并计算盈亏"""
        self.current_price = new_price
        if new_price > self.highest_price:
            self.highest_price = new_price

        self.unrealized_pnl = (new_price - self.entry_price) * self.amount_tokens
        self.unrealized_pnl_pct = (new_price - self.entry_price) / self.entry_price


@dataclass
class PaperTrade:
    """纸交易记录"""
    action: str  # 'buy', 'sell'
    token_address: str
    symbol: str
    price: float
    amount_sol: float
    amount_tokens: float
    timestamp: datetime
    tx_signature: str  # 模拟交易签名
    pnl: float = 0.0
    pnl_pct: float = 0.0
    exit_reason: str = ''


class PaperTrader:
    """
    纸交易器
    模拟真实交易环境，无需真实资金
    """

    def __init__(self, initial_sol: float = 0.5):
        self.initial_sol = initial_sol
        self.balance_sol = initial_sol
        self.positions: Dict[str, PaperPosition] = {}
        self.trade_history: List[PaperTrade] = []
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0

        # 模拟滑点和手续费
        self.slippage_pct = 0.001  # 0.1%
        self.commission_pct = 0.001  # 0.1% (Jupiter fee)

        logger.info(f"Paper Trader initialized with {initial_sol} SOL")

    async def buy(self, token_address: str, amount_sol: float, symbol: str = "Unknown") -> bool:
        """
        模拟买入

        Args:
            token_address: 代币地址
            amount_sol: SOL数量
            symbol: 代币符号

        Returns:
            是否成功
        """
        # 检查余额
        if amount_sol > self.balance_sol:
            logger.warning(f"[PAPER] Insufficient balance: {self.balance_sol:.4f} < {amount_sol:.4f}")
            return False

        # 模拟询价 (简化：假设价格是随机的)
        simulated_price = self._simulate_price(token_address)

        # 考虑滑点和手续费
        effective_sol = amount_sol * (1 - self.commission_pct)
        entry_price = simulated_price * (1 + self.slippage_pct)
        amount_tokens = effective_sol / entry_price

        # 扣除余额
        self.balance_sol -= amount_sol

        # 创建持仓
        position = PaperPosition(
            token_address=token_address,
            symbol=symbol,
            entry_price=entry_price,
            entry_time=datetime.now(),
            amount_tokens=amount_tokens,
            amount_sol=amount_sol,
            current_price=entry_price,
            highest_price=entry_price
        )

        self.positions[token_address] = position

        # 记录交易
        trade = PaperTrade(
            action='buy',
            token_address=token_address,
            symbol=symbol,
            price=entry_price,
            amount_sol=amount_sol,
            amount_tokens=amount_tokens,
            timestamp=datetime.now(),
            tx_signature=f"PAPER_BUY_{self.total_trades}_{token_address[:8]}"
        )
        self.trade_history.append(trade)
        self.total_trades += 1

        logger.success(
            f"[PAPER BUY] {symbol} ({token_address[:8]}...)\n"
            f"  Amount: {amount_sol:.4f} SOL -> {amount_tokens:.2f} tokens\n"
            f"  Price: {entry_price:.10f} SOL/token\n"
            f"  Remaining Balance: {self.balance_sol:.4f} SOL"
        )

        return True

    async def sell(self, token_address: str, percentage: float = 1.0, symbol: str = "Unknown") -> bool:
        """
        模拟卖出

        Args:
            token_address: 代币地址
            percentage: 卖出比例 (0-1)
            symbol: 代币符号

        Returns:
            是否成功
        """
        if token_address not in self.positions:
            logger.warning(f"[PAPER] No position found for {token_address}")
            return False

        position = self.positions[token_address]

        # 更新到当前价格
        current_price = self._simulate_price(token_address)
        position.update_price(current_price)

        # 计算卖出数量
        sell_tokens = position.amount_tokens * percentage
        exit_price = current_price * (1 - self.slippage_pct)
        received_sol = sell_tokens * exit_price * (1 - self.commission_pct)

        # 计算盈亏
        cost_basis = position.amount_sol * percentage
        pnl = received_sol - cost_basis
        pnl_pct = pnl / cost_basis if cost_basis > 0 else 0

        # 更新余额
        self.balance_sol += received_sol

        # 更新持仓
        if percentage >= 0.99:  # 全部卖出
            del self.positions[token_address]
        else:
            position.amount_tokens -= sell_tokens
            position.amount_sol -= cost_basis

        # 更新统计
        self.total_pnl += pnl
        if pnl > 0:
            self.winning_trades += 1

        # 记录交易
        trade = PaperTrade(
            action='sell',
            token_address=token_address,
            symbol=symbol,
            price=exit_price,
            amount_sol=received_sol,
            amount_tokens=sell_tokens,
            timestamp=datetime.now(),
            tx_signature=f"PAPER_SELL_{self.total_trades}_{token_address[:8]}",
            pnl=pnl,
            pnl_pct=pnl_pct,
            exit_reason='manual'
        )
        self.trade_history.append(trade)
        self.total_trades += 1

        logger.success(
            f"[PAPER SELL] {symbol} ({token_address[:8]}...)\n"
            f"  Amount: {sell_tokens:.2f} tokens -> {received_sol:.4f} SOL\n"
            f"  Price: {exit_price:.10f} SOL/token\n"
            f"  PnL: {pnl:.4f} SOL ({pnl_pct:+.2%})\n"
            f"  Balance: {self.balance_sol:.4f} SOL"
        )

        return True

    def _simulate_price(self, token_address: str) -> float:
        """模拟价格（基于token地址的哈希）"""
        # 使用token地址生成一个相对固定的价格
        hash_val = hash(token_address) % 1000000
        base_price = 0.000001 + (hash_val / 1000000) * 0.001

        # 添加随机波动
        volatility = random.uniform(0.95, 1.05)
        return base_price * volatility

    def update_prices(self, price_updates: Dict[str, float]):
        """批量更新价格"""
        for token_address, price in price_updates.items():
            if token_address in self.positions:
                self.positions[token_address].update_price(price)

    def get_position(self, token_address: str) -> Optional[PaperPosition]:
        """获取持仓信息"""
        return self.positions.get(token_address)

    def get_all_positions(self) -> List[PaperPosition]:
        """获取所有持仓"""
        return list(self.positions.values())

    def get_portfolio_value(self) -> Dict:
        """获取组合总价值"""
        positions_value = sum(
            pos.amount_tokens * pos.current_price
            for pos in self.positions.values()
        )

        total_value = self.balance_sol + positions_value
        total_return = (total_value - self.initial_sol) / self.initial_sol

        return {
            'balance_sol': self.balance_sol,
            'positions_value_sol': positions_value,
            'total_value_sol': total_value,
            'total_return_pct': total_return * 100,
            'open_positions': len(self.positions),
            'unrealized_pnl': sum(pos.unrealized_pnl for pos in self.positions.values()),
            'realized_pnl': self.total_pnl
        }

    def get_performance_report(self) -> str:
        """生成性能报告"""
        portfolio = self.get_portfolio_value()
        win_rate = self.winning_trades / max(self.total_trades // 2, 1)  # 只计算完成的交易对

        report = f"""
╔════════════════════════════════════════════════╗
║           纸交易性能报告 (PAPER TRADING)        ║
╠════════════════════════════════════════════════╣
║ 初始资金:        {self.initial_sol:.4f} SOL                    ║
║ 当前余额:        {portfolio['balance_sol']:.4f} SOL                    ║
║ 持仓价值:        {portfolio['positions_value_sol']:.4f} SOL                    ║
║ 总权益:          {portfolio['total_value_sol']:.4f} SOL                    ║
║ 总收益率:        {portfolio['total_return_pct']:+.2f}%                       ║
╠════════════════════════════════════════════════╣
║ 交易统计:                                       ║
║   总交易数:      {self.total_trades:<3}                            ║
║   胜率:          {win_rate*100:.1f}%                              ║
║   已实现盈亏:    {self.total_pnl:+.4f} SOL                    ║
║   未实现盈亏:    {portfolio['unrealized_pnl']:+.4f} SOL                    ║
╠════════════════════════════════════════════════╣
║ 持仓明细 ({portfolio['open_positions']}个):                           ║
"""
        for addr, pos in self.positions.items():
            report += f"║   {pos.symbol[:10]:<10} {pos.unrealized_pnl_pct:+.2%}  {pos.amount_sol:.4f}SOL  ║\n"

        report += "╚════════════════════════════════════════════════╝"

        return report

    def export_trade_history(self, filepath: str):
        """导出交易历史到JSON"""
        data = [asdict(trade) for trade in self.trade_history]
        # 转换datetime为字符串
        for item in data:
            item['timestamp'] = item['timestamp'].isoformat()

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Trade history exported to {filepath}")

    def close(self):
        """关闭纸交易器"""
        logger.info("Paper Trader closed")


class HybridTrader:
    """
    混合交易器
    根据MODE环境变量自动选择纸交易或实盘
    """

    def __init__(self, mode: str = 'paper', initial_sol: float = 0.5):
        self.mode = mode
        self.paper_trader = PaperTrader(initial_sol)
        self.live_trader = None  # 实盘交易器，按需导入

        logger.info(f"Hybrid Trader initialized in {mode.upper()} mode")

    async def buy(self, token_address: str, amount_sol: float, symbol: str = "Unknown"):
        """买入 - 根据模式自动选择"""
        if self.mode == 'paper':
            return await self.paper_trader.buy(token_address, amount_sol, symbol)
        else:
            # 实盘模式
            from .trader import SolanaTrader
            if not self.live_trader:
                self.live_trader = SolanaTrader()
            return await self.live_trader.buy(token_address, amount_sol)

    async def sell(self, token_address: str, percentage: float = 1.0, symbol: str = "Unknown"):
        """卖出 - 根据模式自动选择"""
        if self.mode == 'paper':
            return await self.paper_trader.sell(token_address, percentage, symbol)
        else:
            from .trader import SolanaTrader
            if not self.live_trader:
                self.live_trader = SolanaTrader()
            return await self.live_trader.sell(token_address, percentage)

    def get_portfolio(self):
        """获取组合信息"""
        if self.mode == 'paper':
            return self.paper_trader.get_portfolio_value()
        return {}

    def get_performance_report(self):
        """获取性能报告"""
        if self.mode == 'paper':
            return self.paper_trader.get_performance_report()
        return "Live trading performance not available"

    async def close(self):
        """关闭交易器"""
        self.paper_trader.close()
        if self.live_trader:
            await self.live_trader.close()


# 使用示例
if __name__ == "__main__":
    async def test():
        trader = PaperTrader(initial_sol=0.5)

        # 模拟买入
        await trader.buy(
            token_address="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            amount_sol=0.01,
            symbol="BONK"
        )

        # 显示持仓
        print(trader.get_performance_report())

        # 模拟卖出50%
        await trader.sell(
            token_address="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            percentage=0.5,
            symbol="BONK"
        )

        # 最终报告
        print(trader.get_performance_report())

    asyncio.run(test())
