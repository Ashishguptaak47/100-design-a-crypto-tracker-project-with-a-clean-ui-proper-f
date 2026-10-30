import sqlite3
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

class PortfolioRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    buy_price REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    target_price REAL NOT NULL,
                    condition TEXT CHECK(condition IN ('ABOVE', 'BELOW')) NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get_portfolio(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM portfolio ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_position(self, coin_id: str, symbol: str, name: str, amount: float, buy_price: float) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO portfolio (coin_id, symbol, name, amount, buy_price) VALUES (?, ?, ?, ?, ?)",
                (coin_id.lower(), symbol.upper(), name, float(amount), float(buy_price))
            )
            conn.commit()
            return cursor.lastrowid

    def remove_position(self, position_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM portfolio WHERE id = ?", (position_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_alerts(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_alert(self, coin_id: str, symbol: str, target_price: float, condition: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO alerts (coin_id, symbol, target_price, condition) VALUES (?, ?, ?, ?)",
                (coin_id.lower(), symbol.upper(), float(target_price), condition.upper())
            )
            conn.commit()
            return cursor.lastrowid

    def remove_alert(self, alert_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
            conn.commit()
            return cursor.rowcount > 0

portfolio_repo = PortfolioRepository()
