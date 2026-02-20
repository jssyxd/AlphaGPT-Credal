"""
增强风控模块 - 低资金专用风险控制
包含反欺诈检测、流动性过滤、日本税务提醒
"""

import asyncio
import aiohttp
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from loguru import logger
import json


@dataclass
class RiskConfig:
    """风控配置 - 针对低资金用户优化"""
    # 仓位控制
    max_position_size_pct: float = 0.01  # 每笔交易最多1%
    max_positions: int = 3  # 最多同时持有3个仓位
    min_balance_sol: float = 0.1  # 最低保留0.1 SOL

    # 流动性过滤
    min_liquidity_usd: float = 10000.0  # 最低$10k流动性
    min_volume_24h: float = 5000.0  # 24h最低$5k交易量

    # 止损止盈
    stop_loss_pct: float = 0.05  # 5%止损
    take_profit_target1: float = 0.10  # 10%止盈目标1
    trailing_activation: float = 0.08  # 8%触发移动止盈
    trailing_drop: float = 0.05  # 回撤5%移动止盈

    # 反欺诈
    max_creator_hold_pct: float = 0.20  # 创建者持仓不超过20%
    min_holder_count: int = 50  # 最少50个持有者
    max_snipers_count: int = 10  # 狙击者数量不超过10

    # 日本税务提醒阈值（日元）
    tax_reminder_threshold: float = 50000  # 盈利超5万提醒税务


class RiskEngine:
    """
    风险引擎
    执行全面的风险控制检查
    """

    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
        self.birdeye_api_key = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.total_realized_pnl: float = 0.0

    async def initialize(self):
        """初始化风控引擎"""
        self.session = aiohttp.ClientSession()
        logger.info("Risk Engine initialized")

    async def check_safety(
        self,
        token_address: str,
        liquidity_usd: float,
        birdeye_api_key: str = None
    ) -> Dict:
        """
        执行完整的安全检查

        Returns:
            {
                'is_safe': bool,
                'score': float (0-1),
                'checks': Dict[str, bool],
                'warnings': List[str]
            }
        """
        if birdeye_api_key:
            self.birdeye_api_key = birdeye_api_key

        checks = {}
        warnings = []
        score = 1.0

        # 1. 流动性检查
        if liquidity_usd < self.config.min_liquidity_usd:
            checks['liquidity'] = False
            warnings.append(f"流动性过低: ${liquidity_usd:.0f} < ${self.config.min_liquidity_usd:.0f}")
            score -= 0.3
        else:
            checks['liquidity'] = True

        # 2. 代币安全检查（通过Birdeye）
        token_info = await self._get_token_info(token_address)
        if token_info:
            # 持有者数量
            holder_count = token_info.get('holder_count', 0)
            if holder_count < self.config.min_holder_count:
                checks['holders'] = False
                warnings.append(f"持有者过少: {holder_count} < {self.config.min_holder_count}")
                score -= 0.2
            else:
                checks['holders'] = True

            # 24h交易量
            volume_24h = token_info.get('volume_24h', 0)
            if volume_24h < self.config.min_volume_24h:
                checks['volume'] = False
                warnings.append(f"24h交易量过低: ${volume_24h:.0f}")
                score -= 0.1
            else:
                checks['volume'] = True

            # 创建者持仓检查（反Rug）
            creator_hold_pct = token_info.get('creator_hold_pct', 0)
            if creator_hold_pct > self.config.max_creator_hold_pct:
                checks['creator_hold'] = False
                warnings.append(f"创建者持仓过高: {creator_hold_pct:.1%}")
                score -= 0.3
            else:
                checks['creator_hold'] = True
        else:
            logger.warning(f"无法获取代币信息: {token_address}")
            checks['token_info'] = False
            score -= 0.1

        # 3. 计算最终安全评分
        score = max(0.0, score)
        is_safe = score >= 0.6 and all([
            checks.get('liquidity', False),
            checks.get('creator_hold', True)
        ])

        return {
            'is_safe': is_safe,
            'score': score,
            'checks': checks,
            'warnings': warnings
        }

    def calculate_position_size(self, balance_sol: float) -> float:
        """
        计算仓位大小（SOL）
        遵循1%风险规则
        """
        if balance_sol < self.config.min_balance_sol:
            logger.warning(f"余额过低: {balance_sol:.4f} SOL")
            return 0

        # 保留最低余额
        available = balance_sol - self.config.min_balance_sol

        # 计算1%仓位
        position_size = available * self.config.max_position_size_pct

        # 确保至少有一定大小
        min_trade = 0.01  # 0.01 SOL 最低交易
        if position_size < min_trade:
            position_size = min(min_trade, available * 0.5)

        return max(0, position_size)

    def check_position_exit(
        self,
        entry_price: float,
        current_price: float,
        highest_price: float,
        is_moonbag: bool = False
    ) -> Optional[str]:
        """
        检查是否应该平仓

        Returns:
            'stop_loss', 'take_profit', 'trailing_stop', or None
        """
        pnl_pct = (current_price - entry_price) / entry_price

        # 止损检查
        if pnl_pct <= -self.config.stop_loss_pct:
            return 'stop_loss'

        # 止盈检查（非月亮袋仓位）
        if not is_moonbag and pnl_pct >= self.config.take_profit_target1:
            return 'take_profit'

        # 移动止盈检查
        if highest_price > entry_price:
            max_gain = (highest_price - entry_price) / entry_price

            if max_gain > self.config.trailing_activation:
                drawdown = (highest_price - current_price) / highest_price
                if drawdown > self.config.trailing_drop:
                    return 'trailing_stop'

        return None

    async def _get_token_info(self, token_address: str) -> Optional[Dict]:
        """从Birdeye获取代币信息"""
        if not self.session or not self.birdeye_api_key:
            return None

        try:
            url = f"https://public-api.birdeye.so/public/tokeninfo?address={token_address}"
            headers = {"X-API-KEY": self.birdeye_api_key}

            async with self.session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('data', {})
                else:
                    logger.warning(f"Birdeye API error: {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"获取代币信息失败: {e}")
            return None

    def update_realized_pnl(self, pnl: float):
        """更新已实现盈亏，用于税务提醒"""
        self.total_realized_pnl += pnl

        # 检查是否需要税务提醒
        if self.total_realized_pnl > self.config.tax_reminder_threshold:
            logger.warning(
                f"💰 税务提醒: 已实现盈亏达到 {self.total_realized_pnl:,.0f} JPY\n"
                f"   超过 {self.config.tax_reminder_threshold:,.0f} JPY，请注意日本税务申报！\n"
                f"   申报截止日期: 次年3月15日"
            )

    def get_tax_summary(self) -> Dict:
        """获取税务摘要"""
        tax_rate = self._estimate_tax_rate(self.total_realized_pnl)
        estimated_tax = self.total_realized_pnl * tax_rate

        return {
            'total_profit_jpy': float(self.total_realized_pnl),
            'estimated_tax_rate': float(tax_rate),
            'estimated_tax_jpy': float(estimated_tax),
            'after_tax_profit_jpy': float(self.total_realized_pnl - estimated_tax),
            'filing_required': self.total_realized_pnl > 200000,  # 20万免税额
            'deadline': '次年3月15日'
        }

    def _estimate_tax_rate(self, profit: float) -> float:
        """估算日本税率"""
        if profit <= 0:
            return 0
        elif profit <= 1950000:
            return 0.05
        elif profit <= 3300000:
            return 0.10
        elif profit <= 6950000:
            return 0.20
        elif profit <= 9000000:
            return 0.23
        elif profit <= 18000000:
            return 0.33
        elif profit <= 40000000:
            return 0.40
        else:
            return 0.45

    def get_risk_report(self) -> str:
        """生成风控报告"""
        tax_summary = self.get_tax_summary()

        report = f"""
╔════════════════════════════════════════╗
║         AlphaGPT 风控报告              ║
╠════════════════════════════════════════╣
║ 风控配置:                              ║
║   最大仓位: {self.config.max_position_size_pct:>6.1%}                  ║
║   最大持仓: {self.config.max_positions:>3}个                     ║
║   止损线:   {self.config.stop_loss_pct:>6.1%}                  ║
║   止盈线:   {self.config.take_profit_target1:>6.1%}                  ║
╠════════════════════════════════════════╣
║ 税务摘要:                              ║
║   已实现盈亏: {tax_summary['total_profit_jpy']:>10,.0f} JPY         ║
║   预估税率:   {tax_summary['estimated_tax_rate']:>10.1%}            ║
║   预估税额:   {tax_summary['estimated_tax_jpy']:>10,.0f} JPY         ║
║   税后盈利:   {tax_summary['after_tax_profit_jpy']:>10,.0f} JPY         ║
║   需要申报:   {'是' if tax_summary['filing_required'] else '否':>10}            ║
╚════════════════════════════════════════╝
"""
        return report

    async def close(self):
        """关闭风控引擎"""
        if self.session:
            await self.session.close()


# 同步包装函数
def calculate_position_size_sync(balance_sol: float) -> float:
    """同步计算仓位大小"""
    engine = RiskEngine()
    return engine.calculate_position_size(balance_sol)


def check_rug_risk_indicators(token_data: Dict) -> Dict:
    """
    快速检查RUG风险指标
    无需API调用，基于已有数据
    """
    risk_score = 0
    warnings = []

    # 检查流动性锁定
    if token_data.get('liquidity_locked', True) == False:
        risk_score += 30
        warnings.append("流动性未锁定")

    # 检查合约是否放弃
    if token_data.get('contract_renounced', False) == False:
        risk_score += 20
        warnings.append("合约未放弃")

    # 检查薄荷功能
    if token_data.get('mint_enabled', True):
        risk_score += 40
        warnings.append("合约仍可铸币")

    # 检查黑名单功能
    if token_data.get('blacklist_enabled', True):
        risk_score += 20
        warnings.append("合约有黑名单功能")

    return {
        'risk_score': min(risk_score, 100),
        'risk_level': 'HIGH' if risk_score > 60 else 'MEDIUM' if risk_score > 30 else 'LOW',
        'warnings': warnings,
        'is_safe': risk_score < 50
    }


if __name__ == "__main__":
    # 测试风控引擎
    engine = RiskEngine()

    # 测试仓位计算
    balance = 0.32  # SOL
    position = engine.calculate_position_size(balance)
    print(f"余额: {balance} SOL")
    print(f"建议仓位: {position:.4f} SOL ({position/balance*100:.1f}%)")

    # 测试平仓检查
    entry = 100
    current = 115
    highest = 120

    exit_signal = engine.check_position_exit(entry, current, highest)
    print(f"\n入场价: {entry}, 当前: {current}, 最高: {highest}")
    print(f"平仓信号: {exit_signal}")

    # 测试税务计算
    engine.update_realized_pnl(100000)  # 10万日元
    print("\n" + engine.get_risk_report())

    # 测试RUG风险检查
    test_token = {
        'liquidity_locked': False,
        'contract_renounced': False,
        'mint_enabled': True,
        'blacklist_enabled': False
    }
    risk = check_rug_risk_indicators(test_token)
    print(f"\nRUG风险评分: {risk['risk_score']}/100 ({risk['risk_level']})")
    print(f"警告: {risk['warnings']}")
