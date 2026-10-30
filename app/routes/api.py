from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.services.crypto_api import crypto_service
from app.services.portfolio import portfolio_repo
from app.config import SUPPORTED_CURRENCIES

router = APIRouter(prefix="/api")

class PositionCreate(BaseModel):
    coin_id: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    buy_price: float = Field(..., gt=0)

class AlertCreate(BaseModel):
    coin_id: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1)
    target_price: float = Field(..., gt=0)
    condition: str = Field(..., pattern="^(ABOVE|BELOW)$")

@router.get("/markets")
async def get_markets(currency: str = Query("usd", regex="^(usd|eur|gbp)$")):
    coins = await crypto_service.get_markets(currency)
    return {"currency": currency, "coins": coins}

@router.get("/portfolio")
async def get_portfolio_summary(currency: str = Query("usd", regex="^(usd|eur|gbp)$")):
    coins = await crypto_service.get_markets(currency)
    price_map = {c["id"].lower(): c.get("current_price", 0.0) for c in coins}
    positions = portfolio_repo.get_portfolio()

    total_invested = 0.0
    total_current_value = 0.0
    enriched = []

    for p in positions:
        curr_price = price_map.get(p["coin_id"].lower(), p["buy_price"])
        invested = p["amount"] * p["buy_price"]
        curr_val = p["amount"] * curr_price
        pnl = curr_val - invested
        pnl_perc = ((pnl / invested) * 100) if invested > 0 else 0.0

        total_invested += invested
        total_current_value += curr_val

        enriched.append({
            **p,
            "current_price": curr_price,
            "current_value": round(curr_val, 2),
            "pnl": round(pnl, 2),
            "pnl_percentage": round(pnl_perc, 2)
        })

    total_pnl = total_current_value - total_invested
    total_pnl_perc = ((total_pnl / total_invested) * 100) if total_invested > 0 else 0.0

    return {
        "summary": {
            "total_invested": round(total_invested, 2),
            "total_value": round(total_current_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_percentage": round(total_pnl_perc, 2),
            "currency_symbol": SUPPORTED_CURRENCIES[currency]["symbol"]
        },
        "positions": enriched
    }

@router.post("/portfolio")
async def add_position(item: PositionCreate):
    pid = portfolio_repo.add_position(item.coin_id, item.symbol, item.name, item.amount, item.buy_price)
    return {"status": "success", "id": pid}

@router.delete("/portfolio/{position_id}")
async def delete_position(position_id: int):
    deleted = portfolio_repo.remove_position(position_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Position not found")
    return {"status": "success", "id": position_id}

@router.get("/alerts")
async def get_alerts():
    coins = await crypto_service.get_markets("usd")
    price_map = {c["id"].lower(): c.get("current_price", 0.0) for c in coins}
    alerts = portfolio_repo.get_alerts()
    enriched_alerts = []
    for a in alerts:
        curr_price = price_map.get(a["coin_id"].lower(), 0.0)
        is_triggered = (
            (a["condition"] == "ABOVE" and curr_price >= a["target_price"]) or
            (a["condition"] == "BELOW" and curr_price <= a["target_price"])
        )
        enriched_alerts.append({**a, "current_price": curr_price, "triggered": is_triggered})
    return enriched_alerts

@router.post("/alerts")
async def add_alert(item: AlertCreate):
    aid = portfolio_repo.add_alert(item.coin_id, item.symbol, item.target_price, item.condition)
    return {"status": "success", "id": aid}

@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int):
    deleted = portfolio_repo.remove_alert(alert_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "id": alert_id}
