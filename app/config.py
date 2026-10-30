import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.getenv("CRYPTO_DB_PATH", str(BASE_DIR / "crypto_tracker.db"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "45"))

SUPPORTED_CURRENCIES = {
    "usd": {"symbol": "$", "rate": 1.0},
    "eur": {"symbol": "€", "rate": 0.92},
    "gbp": {"symbol": "£", "rate": 0.79},
}
