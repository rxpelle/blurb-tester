# Trading Bots Information

## Overview
User has two automated trading bots running in Docker containers on this machine.

## Bots

### 1. Crypto Trading Bot
- **Container Name:** `trading-bot`
- **Container ID:** 681106970f8a
- **Image:** `frozen-exoplanet-trading-bot`
- **Status:** Running (check with `docker ps`)
- **Strategy:** Enhanced-v3 multi-pair trading
- **Command:** `python multi_pair_b...`
- **Trading Pairs:** BTC/USD, ETH/USD, SOL/USD, PEPE/USD, WIF/USD, DOGE/USD
- **Database:** `/app/trades.db` (SQLite) - contains trades and daily_summary tables
- **Performance Check:**
  ```bash
  docker logs trading-bot --tail 100
  docker exec trading-bot python3 << 'EOF'
  import sqlite3
  conn = sqlite3.connect("/app/trades.db")
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM trades ORDER BY timestamp")
  # Calculate PnL from trades
  EOF
  ```

### 2. Stock Trading Bot
- **Container Name:** `stock-trading-bot`
- **Container ID:** d3feec3be457
- **Image:** `stock-trader-stock-bot`
- **Status:** Running, Healthy (check with `docker ps`)
- **Strategy:** Momentum Rotation Strategy
- **Mode:** LIVE trading via Alpaca API
- **Trading Platform:** Alpaca
- **Max Positions:** 4 stocks
- **Rebalance Schedule:** Weekly on Mondays @ 09:35 AM PST
- **Stock Universe:** 30 tech/growth stocks (AAPL, GOOGL, AMZN, NVDA, etc.)
- **Account Balance:** Check with `docker logs stock-trading-bot --tail 100`
- **Performance Check:**
  ```bash
  docker logs stock-trading-bot --tail 100 | grep "Portfolio Value"
  ```

### 3. Trading Dashboard
- **Container Name:** `trading-dashboard`
- **Container ID:** b1b20d021c95
- **Image:** `frozen-exoplanet-dashboard`
- **Status:** Running
- **Access:** http://localhost:5001
- **API Endpoints:**
  - http://localhost:5001/api/stats
  - http://localhost:5001/api/trades

## Quick Commands

### Check if bots are running:
```bash
docker ps -a
```

### View crypto bot logs:
```bash
docker logs trading-bot --tail 100
```

### View stock bot logs:
```bash
docker logs stock-trading-bot --tail 100
```

### Check crypto bot returns:
```bash
docker exec trading-bot python3 << 'EOF'
import sqlite3
conn = sqlite3.connect("/app/trades.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM trades ORDER BY timestamp")
trades = cursor.fetchall()
# Process trades to calculate PnL
EOF
```

### Check stock bot status:
```bash
docker logs stock-trading-bot --tail 50 | grep "Portfolio Value"
```

## Notes
- Both bots are configured and running autonomously
- Crypto bot uses a database to track trades
- Stock bot rebalances weekly on Monday mornings
- Dashboard provides web interface for monitoring
- All bots run in Docker containers on the local machine
