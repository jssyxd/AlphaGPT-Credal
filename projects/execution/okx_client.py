"""
AlphaGPT OKX Client
OKX API integration for simulation and live trading
"""
import os
import time
import hmac
import hashlib
import base64
import requests
from typing import Dict, Optional, List
from dotenv import load_dotenv

load_dotenv()


class OKXClient:
    """OKX API client for trading"""

    def __init__(self, api_key: str = None, secret_key: str = None, passphrase: str = None, mode: str = "simulated"):
        self.api_key = api_key or os.getenv("OKX_API_KEY", "")
        self.secret_key = secret_key or os.getenv("OKX_SECRET_KEY", "")
        self.passphrase = passphrase or os.getenv("OKX_PASSPHRASE", "")
        self.mode = mode  # "simulated" or "live"
        self.base_url = "https://www.okx.com"
        self.simulated_balance = float(os.getenv("SIMULATED_BALANCE", "10000"))

    def _sign(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate OKX signature"""
        message = timestamp + method + path + body
        mac = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode()

    def _request(self, method: str, path: str, body: str = "") -> Dict:
        """Make authenticated request to OKX API"""
        if not self.api_key:
            return {"error": "API key not configured"}

        timestamp = str(int(time.time()))
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": self._sign(timestamp, method, path, body),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }

        url = self.base_url + path
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, json=body and eval(body), timeout=10)

            return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            return {"error": str(e)}

    def get_balance(self) -> Dict:
        """Get account balance"""
        if self.mode == "simulated":
            return {
                "code": "0",
                "data": [{"availBal": str(self.simulated_balance), "frozenBal": "0"}]
            }

        return self._request("GET", "/api/v5/account/balance")

    def place_order(self, symbol: str, side: str, order_type: str, size: str, price: str = "") -> Dict:
        """Place an order"""
        if self.mode == "simulated":
            return {
                "code": "0",
                "data": [{"ordId": f"sim_{int(time.time())}", "sCode": "0"}],
                "simulated": True
            }

        path = "/api/v5/trade/order"
        body = {
            "instId": symbol,
            "tdMode": "cash",
            "side": side,
            "ordType": order_type,
            "sz": size,
            "px": price
        }

        return self._request("POST", path, str(body))

    def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an order"""
        if self.mode == "simulated":
            return {"code": "0", "data": [{"ordId": order_id}], "simulated": True}

        path = "/api/v5/trade/cancel-order"
        body = {"instId": symbol, "ordId": order_id}

        return self._request("POST", path, str(body))

    def get_positions(self) -> Dict:
        """Get open positions"""
        if self.mode == "simulated":
            return {"code": "0", "data": [], "simulated": True}

        path = "/api/v5/account/positions"
        return self._request("GET", path)

    def get_ticker(self, symbol: str) -> Dict:
        """Get ticker for a symbol"""
        if self.mode == "simulated":
            return {
                "code": "0",
                "data": [{"last": "100", "bidPx": "99", "askPx": "101"}]
            }

        path = f"/api/v5/market/ticker?instId={symbol}"
        return self._request("GET", path)


# Singleton
_okx_client = None


def get_okx_client(mode: str = None) -> OKXClient:
    """Get OKX client singleton"""
    global _okx_client
    if _okx_client is None:
        _okx_client = OKXClient(mode=mode or os.getenv("OKX_MODE", "simulated"))
    return _okx_client
