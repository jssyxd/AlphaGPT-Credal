"""
AlphaGPT Trading Engine
Combines Jupiter, OKX, and Telegram for complete trading
"""
import os
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv

from execution.paper_trader import PaperTrader
from execution.okx_client import get_okx_client
from execution.telegram_bot import get_telegram_bot
from data_pipeline.db import get_db_manager

load_dotenv()


class TradingEngine:
    """Main trading engine that coordinates all execution components"""

    def __init__(self, mode: str = None):
        self.mode = mode or get_db_manager().get_mode() or "paper"
        self.paper_trader = PaperTrader()
        self.okx_client = get_okx_client(self.mode)
        self.telegram = get_telegram_bot()

        # Risk parameters
        self.max_position_pct = float(get_db_manager().get_setting("max_position_size_pct", "0.01"))
        self.max_positions = int(get_db_manager().get_setting("max_positions", "3"))
        self.stop_loss_pct = float(get_db_manager().get_setting("stop_loss_pct", "0.05"))
        self.take_profit_pct = float(get_db_manager().get_setting("take_profit_pct", "0.10"))

    def check_risk_limits(self, token_address: str, token_data: Dict) -> tuple[bool, str]:
        """Check if trade passes risk filters"""
        # Check liquidity
        min_liquidity = float(get_db_manager().get_setting("min_liquidity", "10000"))
        if token_data.get("liquidity", 0) < min_liquidity:
            return False, f"Liquidity ${token_data.get('liquidity', 0)} < ${min_liquidity}"

        # Check holders
        min_holders = int(get_db_manager().get_setting("min_holders", "50"))
        if token_data.get("holders", 0) < min_holders:
            return False, f"Holders {token_data.get('holders', 0)} < {min_holders}"

        # Check creator percent
        max_creator = float(get_db_manager().get_setting("max_creator_percent", "20"))
        if token_data.get("creator_percent", 100) > max_creator:
            return False, f"Creator {token_data.get('creator_percent', 0)}% > {max_creator}%"

        return True, "OK"

    async def execute_buy(self, token_address: str, symbol: str, amount_sol: float, price: float, token_data: Dict) -> Dict:
        """Execute a buy order"""
        # Check risk limits
        passed, reason = self.check_risk_limits(token_address, token_data)
        if not passed:
            self.telegram.send_alert("warning", f"Buy blocked: {reason}")
            return {"status": "rejected", "reason": reason}

        # Calculate position size
        amount_tokens = amount_sol / price if price > 0 else 0
        stop_loss_price = price * (1 - self.stop_loss_pct)
        take_profit_price = price * (1 + self.take_profit_pct)

        # Execute based on mode
        if self.mode == "paper":
            result = self.paper_trader.open_position(
                token_address=token_address,
                symbol=symbol,
                entry_price=price,
                amount_sol=amount_sol,
                amount_tokens=amount_tokens,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price
            )
        else:
            result = self.okx_client.place_order(
                symbol=symbol,
                side="buy",
                order_type="market",
                size=str(amount_tokens)
            )

        # Send notification
        self.telegram.send_trade_notification({
            "action": "BUY",
            "symbol": symbol,
            "amount_sol": amount_sol,
            "price": price,
            "pnl": 0
        })

        return result

    async def execute_sell(self, token_address: str, symbol: str, position_id: int, current_price: float) -> Dict:
        """Execute a sell order"""
        # Get position from database
        db = get_db_manager()
        supabase = db.supabase
        response = supabase.table("positions").select("*").eq("id", position_id).execute()

        if not response.data:
            return {"status": "error", "reason": "Position not found"}

        position = response.data[0]
        entry_price = position["entry_price"]
        pnl = (current_price - entry_price) / entry_price

        # Execute based on mode
        if self.mode == "paper":
            result = self.paper_trader.close_position(
                position_id=position_id,
                exit_price=current_price,
                pnl=pnl
            )
        else:
            result = self.okx_client.place_order(
                symbol=symbol,
                side="sell",
                order_type="market",
                size=str(position["amount_tokens"])
            )

        # Send notification
        self.telegram.send_trade_notification({
            "action": "SELL",
            "symbol": symbol,
            "amount_sol": position["amount_sol"],
            "price": current_price,
            "pnl": pnl * position["amount_sol"]
        })

        return result

    async def check_positions(self, current_prices: Dict[str, float]) -> List[Dict]:
        """Check all positions for stop loss / take profit"""
        db = get_db_manager()
        supabase = db.supabase
        response = supabase.table("positions").select("*").eq("status", "open").execute()

        to_close = []
        for position in response.data:
            token = position["symbol"]
            current_price = current_prices.get(token, 0)
            if current_price == 0:
                continue

            entry_price = position["entry_price"]
            pnl_pct = (current_price - entry_price) / entry_price

            # Check stop loss
            if pnl_pct <= -self.stop_loss_pct:
                to_close.append({
                    "position_id": position["id"],
                    "token_address": position["token_address"],
                    "symbol": token,
                    "reason": "stop_loss",
                    "pnl_pct": pnl_pct
                })

            # Check take profit
            elif pnl_pct >= self.take_profit_pct:
                to_close.append({
                    "position_id": position["id"],
                    "token_address": position["token_address"],
                    "symbol": token,
                    "reason": "take_profit",
                    "pnl_pct": pnl_pct
                })

        return to_close


# Singleton
_trading_engine = None


def get_trading_engine(mode: str = None) -> TradingEngine:
    """Get trading engine singleton"""
    global _trading_engine
    if _trading_engine is None:
        _trading_engine = TradingEngine(mode=mode)
    return _trading_engine
