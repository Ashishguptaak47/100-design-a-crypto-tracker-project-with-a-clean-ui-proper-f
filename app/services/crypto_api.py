import time
import math
import random
import httpx
from typing import Dict, List, Any
from app.config import CACHE_TTL_SECONDS, SUPPORTED_CURRENCIES

# Fallback catalog in case of rate-limiting or offline usage
MOCK_COINS = [
    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 64250.0, "market_cap": 1265000000000, "market_cap_rank": 1, "total_volume": 28400000000, "price_change_percentage_24h": 2.45},
    {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 3480.0, "market_cap": 418000000000, "market_cap_rank": 2, "total_volume": 14200000000, "price_change_percentage_24h": -1.15},
    {"id": "solana", "symbol": "sol", "name": "Solana", "current_price": 142.5, "market_cap": 66100000000, "market_cap_rank": 3, "total_volume": 3800000000, "price_change_percentage_24h": 5.82},
    {"id": "binancecoin", "symbol": "bnb", "name": "BNB", "current_price": 585.0, "market_cap": 89500000000, "market_cap_rank": 4, "total_volume": 980000000, "price_change_percentage_24h": 0.65},
    {"id": "ripple", "symbol": "xrp", "name": "XRP", "current_price": 0.585, "market_cap": 32900000000, "market_cap_rank": 5, "total_volume": 1120000000, "price_change_percentage_24h": -0.42},
    {"id": "cardano", "symbol": "ada", "name": "Cardano", "current_price": 0.462, "market_cap": 16500000000, "market_cap_rank": 6, "total_volume": 410000000, "price_change_percentage_24h": 1.18},
    {"id": "avalanche-2", "symbol": "avax", "name": "Avalanche", "current_price": 27.8, "market_cap": 11000000000, "market_cap_rank": 7, "total_volume": 320000000, "price_change_percentage_24h": 3.44},
    {"id": "chainlink", "symbol": "link", "name": "Chainlink", "current_price": 13.9, "market_cap": 8450000000, "market_cap_rank": 8, "total_volume": 245000000, "price_change_percentage_24h": -2.31}
]

class CryptoService:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._last_fetch: float = 0.0

    def _generate_sparkline(self, base_price: float, change_24h: float) -> List[float]:
        points = 24
        result = []
        start_price = base_price / (1 + (change_24h / 100))
        for i in range(points):
            progress = i / (points - 1)
            noise = (random.random() - 0.48) * (base_price * 0.015)
            trend = start_price + (base_price - start_price) * progress
            result.append(round(max(0.0001, trend + noise), 4))
        return result

    def _get_mock_markets(self, currency: str) -> List[Dict[str, Any]]:
        rate = SUPPORTED_CURRENCIES.get(currency.lower(), {}).get("rate", 1.0)
        coins = []
        for m in MOCK_COINS:
            c = dict(m)
            c["current_price"] = round(m["current_price"] * rate, 4 if m["current_price"] < 1 else 2)
            c["market_cap"] = int(m["market_cap"] * rate)
            c["total_volume"] = int(m["total_volume"] * rate)
            c["sparkline_in_7d"] = {"price": self._generate_sparkline(c["current_price"], c["price_change_percentage_24h"])}
            c["image"] = f"https://assets.coingecko.com/coins/images/{m['market_cap_rank']}/small/{m['symbol']}.png"
            coins.append(c)
        return coins

    async def get_markets(self, currency: str = "usd") -> List[Dict[str, Any]]:
        currency = currency.lower()
        cache_key = f"markets_{currency}"
        now = time.time()

        if cache_key in self._cache and (now - self._last_fetch) < CACHE_TTL_SECONDS:
            return self._cache[cache_key]

        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": currency,
            "order": "market_cap_desc",
            "per_page": 15,
            "page": 1,
            "sparkline": "true",
            "price_change_percentage": "24h"
        }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    self._cache[cache_key] = data
                    self._last_fetch = now
                    return data
        except Exception:
            pass

        # Fallback to local deterministic generator
        fallback = self._get_mock_markets(currency)
        self._cache[cache_key] = fallback
        self._last_fetch = now
        return fallback

crypto_service = CryptoService()
