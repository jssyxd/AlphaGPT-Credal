"""
AlphaGPT Telegram Bot
Sends trading signals and reports to Telegram
"""
import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class TelegramBot:
    """Telegram bot for sending signals and reports"""

    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.proxy = os.getenv("HTTP_PROXY", os.getenv("HTTP_PROXY", ""))

    def _send_request(self, method: str, data: Dict = None) -> Dict:
        """Send request to Telegram API"""
        if not self.token or not self.chat_id:
            return {"ok": False, "error": "Bot token or chat ID not configured"}

        url = f"{self.api_url}/{method}"
        try:
            kwargs = {"json": data, "timeout": 10}
            if self.proxy:
                kwargs["proxies"] = {"http": self.proxy, "https": self.proxy}

            response = requests.post(url, **kwargs)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_message(self, text: str, parse_mode: str = "Markdown") -> Dict:
        """Send a message"""
        if not self.token or not self.chat_id:
            print(f"[Telegram Mock] {text}")
            return {"ok": True, "mock": True}

        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }

        return self._send_request("sendMessage", data)

    def send_signal(self, signal: Dict) -> Dict:
        """Send a trading signal"""
        token = signal.get("symbol", "UNKNOWN")
        action = signal.get("action", "UNKNOWN")
        price = signal.get("price", 0)
        score = signal.get("score", 0)
        uncertainty = signal.get("uncertainty", 1.0)
        reasons = signal.get("reasons", "")

        text = f"""📡 *AlphaGPT Trading Signal*

*{action.upper()}* {token}
💰 Price: ${price:.6f}
📊 Score: {score:.2f}
🎯 Uncertainty: {uncertainty:.2f}

📝 *Reasons:*
{reasons}
"""

        return self.send_message(text)

    def send_trade_notification(self, trade: Dict) -> Dict:
        """Send trade notification"""
        action = trade.get("action", "UNKNOWN")
        symbol = trade.get("symbol", "UNKNOWN")
        amount = trade.get("amount_sol", 0)
        price = trade.get("price", 0)
        pnl = trade.get("pnl", 0)

        emoji = "🟢" if action == "BUY" else "🔴"
        pnl_emoji = "📈" if pnl > 0 else "📉" if pnl < 0 else "➖"

        text = f"""{emoji} *Trade Executed*

*{action}* {amount:.4f} SOL of {symbol}
💵 Price: ${price:.6f}
{pnl_emoji} PnL: ${pnl:.2f}
"""

        return self.send_message(text)

    def send_daily_report(self, report: Dict) -> Dict:
        """Send daily report"""
        date = report.get("date", "Unknown")
        total_pnl = report.get("total_pnl", 0)
        trade_count = report.get("trade_count", 0)
        win_count = report.get("win_count", 0)
        loss_count = report.get("loss_count", 0)
        active_positions = report.get("active_positions", 0)

        win_rate = (win_count / trade_count * 100) if trade_count > 0 else 0
        pnl_emoji = "📈" if total_pnl > 0 else "📉"

        text = f"""📊 *AlphaGPT Daily Report* - {date}

{pnl_emoji} *Total PnL:* ${total_pnl:.2f}
📊 *Trades:* {trade_count} ({win_count}W / {loss_count}L)
🎯 *Win Rate:* {win_rate:.1f}%
💼 *Active Positions:* {active_positions}
"""

        return self.send_message(text)

    def send_alert(self, alert_type: str, message: str) -> Dict:
        """Send alert"""
        emoji = {
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️"
        }.get(alert_type, "ℹ️")

        text = f"""{emoji} *AlphaGPT Alert*

{message}
"""

        return self.send_message(text)


# Singleton
_telegram_bot = None


def get_telegram_bot() -> TelegramBot:
    """Get Telegram bot singleton"""
    global _telegram_bot
    if _telegram_bot is None:
        _telegram_bot = TelegramBot()
    return _telegram_bot
