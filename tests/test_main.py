import os
import pytest
from fastapi.testclient import TestClient

# Point database to temporary test db file before loading app
os.environ["CRYPTO_DB_PATH"] = ":memory:"
os.environ["AUTO_OPEN"] = "false"

from main import app
from app.services.portfolio import portfolio_repo

@pytest.fixture(autouse=True)
def setup_clean_db():
    portfolio_repo.init_db()
    yield

client = TestClient(app)

def test_read_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "Apex" in response.text
    assert "ApexCrypto Tracker" in response.text

def test_get_markets():
    response = client.get("/api/markets?currency=usd")
    assert response.status_code == 200
    data = response.json()
    assert "coins" in data
    assert len(data["coins"]) > 0
    first_coin = data["coins"][0]
    assert "current_price" in first_coin
    assert "symbol" in first_coin

def test_portfolio_lifecycle():
    # 1. Add position
    create_payload = {
        "coin_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "amount": 1.5,
        "buy_price": 50000.0
    }
    post_res = client.post("/api/portfolio", json=create_payload)
    assert post_res.status_code == 200
    pos_id = post_res.json().get("id")
    assert pos_id is not None

    # 2. Get portfolio summary
    summary_res = client.get("/api/portfolio?currency=usd")
    assert summary_res.status_code == 200
    data = summary_res.json()
    assert "summary" in data
    assert data["summary"]["total_invested"] == 75000.0
    assert len(data["positions"]) == 1
    assert data["positions"][0]["id"] == pos_id

    # 3. Delete position
    del_res = client.delete(f"/api/portfolio/{pos_id}")
    assert del_res.status_code == 200

    # 4. Verify clean portfolio
    after_res = client.get("/api/portfolio?currency=usd")
    assert len(after_res.json()["positions"]) == 0

def test_alerts_lifecycle():
    alert_payload = {
        "coin_id": "solana",
        "symbol": "SOL",
        "target_price": 100.0,
        "condition": "ABOVE"
    }
    post_res = client.post("/api/alerts", json=alert_payload)
    assert post_res.status_code == 200
    alert_id = post_res.json().get("id")
    assert alert_id is not None

    get_res = client.get("/api/alerts")
    assert get_res.status_code == 200
    alerts = get_res.json()
    assert len(alerts) >= 1
    assert alerts[0]["symbol"] == "SOL"

    del_res = client.delete(f"/api/alerts/{alert_id}")
    assert del_res.status_code == 200
