# ApexCrypto - Modern Crypto Tracker & Portfolio Manager

A full-featured cryptocurrency tracker and personal portfolio dashboard built with FastAPI, SQLite, and modern responsive frontend (Tailwind CSS + Chart.js).

## Features
- **Live Market Feed**: Real-time prices, 24h change, 7-day sparklines, market cap, and volume with CoinGecko API integration.
- **Resilient Fallback Engine**: Built-in in-memory caching and automatic synthetic data fallback if public API rate limits (HTTP 429) are encountered.
- **Portfolio Tracker**: Record transactions, monitor average buy prices, live asset values, and dynamic profit/loss calculation.
- **Price Alerts**: Set target thresholds (above/below price triggers) with real-time status checking.
- **Multi-Currency Support**: Switch seamlessly between USD ($), EUR (€), and GBP (£).
- **Zero-Dependency Frontend**: Responsive dark-mode dashboard without heavy Node.js toolchains.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. Open your browser at `http://localhost:8000` (it will attempt to open automatically).

## Running Tests
```bash
pytest
```
