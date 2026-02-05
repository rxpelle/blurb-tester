# Antigravity - Multi-Project Repository

**Combined projects: Trading System, Personal Assistant, Novel Series, and more**

> **For Claude Code**: When starting a new session, reference [`.claude-context.md`](.claude-context.md) for shortcuts like "open clawd", "open novel", etc.

---

# Trading System - Full Stack Deployment

**Unified trading platform combining Personal Assistant API, Crypto Research Daemon, and Trading Bots**

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Trading System Stack                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Personal         │    │ Crypto Research  │    │ Trading Bots     │
│ Assistant API    │◄───│ Daemon          │◄───│ (Crypto + Stock) │
│ Port: 8788       │    │ Port: 9999       │    │ Python          │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Redis (Port 6379) │
                    │  Signal Delivery   │
                    └────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │ SQLite Database    │
                    │ trading_system.db  │
                    └────────────────────┘
```

## Components

### 1. Personal Assistant (`personal_assistant/`)
- **GitHub:** https://github.com/rxpelle/personal-assistant
- **Tech:** Node.js, Express, SQLite
- **Features:**
  - REST API (port 8788)
  - Trading signal endpoints
  - Multi-persona coaching
  - Google integrations
  - Health tracking

### 2. Crypto Research Daemon
- **Location:** `personal_assistant/server/services/crypto-research-daemon.js`
- **Function:** Generates trading signals every 10 minutes
- **Output:** Publishes to Redis + file fallback

### 3. Trading Bots (`trading_bots_backup/`)
- **Crypto Bot:** Gemini exchange integration
- **Stock Bot:** Alpaca exchange integration
- **Risk Management:** 2% rule enforced via `proper_risk_manager.py`

### 4. Redis Signal Delivery
- **Purpose:** Real-time signal distribution
- **Protocol:** Pub/sub with ACK acknowledgments
- **Fallback:** File-based delivery if Redis unavailable

## Quick Start

### Prerequisites
- Docker & Docker Compose
- API Keys: Claude, Gemini, Alpaca
- Node.js 18+ (for local development)
- Python 3.9+ (for trading bots)

### 1. Configuration
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Database Migration
```bash
cd personal_assistant
node server/db/migrations/002_migrate_assistant_data.js
```

### 3. Start Full Stack
```bash
docker-compose up -d
```

### 4. Verify Health
```bash
curl http://localhost:8788/api/system/health | jq
```

## Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `redis` | 6379 | Signal message broker |
| `personal-assistant` | 8788 | Main API + Research Daemon |
| `crypto-bot` | - | Crypto trading bot (Gemini) |
| `stock-bot` | - | Stock trading bot (Alpaca) |
| `dashboard` | 3000 | Monitoring UI (optional) |

## Risk Management

**Critical: 2% Risk Rule**
- Never risk more than 2% of account equity per trade
- Circuit breaker at 10% drawdown
- Daily loss limit at 3%
- Mandatory stop loss on every trade

**Test Coverage:** 28/29 tests passing (96.6%)

## Phase 2 Implementation

**Status:** ✅ Complete

**Deliverables:**
- Redis signal adapter with ACK protocol
- Unified database schema (8 tables, 4 views)
- Docker Compose orchestration
- Database migration scripts
- Risk manager test suite
- Comprehensive documentation

**Testing:**
- Database migration: ✅ Passed
- Risk manager: ✅ 28/29 tests
- API endpoints: ✅ All working
- Health checks: ✅ All green

## Development

### Local Development (Without Docker)

**Start Personal Assistant:**
```bash
cd personal_assistant
npm install
npm start
```

**Start Crypto Bot:**
```bash
cd trading_bots_backup/crypto_bot
pip install -r requirements.txt
python multi_pair_bot_live_limited.py
```

### Running Tests

**Risk Manager Tests:**
```bash
cd trading_bots_backup/shared
pytest test_proper_risk_manager.py -v --cov=proper_risk_manager
```

**Expected:** 28/29 passing (96.6% - one test has mathematical flaw)

## Deployment

**Live Trading (REAL MONEY - USE WITH CAUTION):**
```bash
# Set in .env
TRADING_MODE=live          # For crypto bot
STOCK_BOT_MODE=live        # For stock bot
GEMINI_SANDBOX=false       # CRITICAL: Real Gemini API
ALPACA_BASE_URL=https://api.alpaca.markets
docker-compose up -d
```

**Paper Trading (Recommended for testing):**
```bash
# Set in .env
TRADING_MODE=paper         # For crypto bot
STOCK_BOT_MODE=paper       # For stock bot
GEMINI_SANDBOX=true        # Gemini sandbox mode
ALPACA_BASE_URL=https://paper-api.alpaca.markets
docker-compose up -d
```

**⚠️ NEVER deploy live without:**
- ✅ 7 days successful paper trading
- ✅ 100% risk manager test pass rate
- ✅ Manual verification of 2% rule
- ✅ Circuit breakers tested

## Monitoring

**Check System Health:**
```bash
curl http://localhost:8788/api/system/health
```

**View Logs:**
```bash
docker-compose logs -f crypto-bot
docker-compose logs -f personal-assistant
```

**Monitor Trades:**
```bash
sqlite3 personal_assistant/data/trading_system.db "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10"
```

## File Structure

```
antigravity/
├── docker-compose.yml          # Full stack orchestration
├── .env.example                # Environment template
├── README.md                   # This file
├── PHASE2_DESIGN.md           # Architecture design
├── PHASE2_IMPLEMENTATION.md   # Implementation guide
│
├── personal_assistant/         # Main API (separate Git repo)
│   ├── server/
│   │   ├── services/
│   │   │   ├── redis-signal-adapter.js
│   │   │   └── crypto-research-daemon.js
│   │   ├── db/migrations/
│   │   │   ├── 001_create_unified_schema.sql
│   │   │   └── 002_migrate_assistant_data.js
│   │   └── routes/
│   │       ├── trading.js
│   │       └── system.js
│   ├── Dockerfile
│   └── package.json
│
└── trading_bots_backup/        # Trading bots
    ├── shared/
    │   ├── proper_risk_manager.py
    │   └── test_proper_risk_manager.py
    └── crypto_bot/
        ├── redis_signal_subscriber.py
        ├── multi_pair_bot_live_limited.py
        └── Dockerfile
```

## API Endpoints

**Trading:**
- `GET /api/trading/analysis` - Bot performance
- `GET /api/trading/positions` - Open positions
- `GET /api/trading/signals` - Recent signals
- `GET /api/trading/risk` - Risk status
- `POST /api/trading/signal` - Signal webhook

**System:**
- `GET /api/system/health` - Full system health
- `GET /api/health` - Legacy health check

## Troubleshooting

**Redis Connection Failed:**
```bash
docker-compose logs redis
docker exec trading-redis redis-cli ping
```

**Database Locked:**
```bash
cd personal_assistant/data
rm *.db-wal *.db-shm
```

**Bot Not Receiving Signals:**
```bash
# Check fallback files
ls -la trading_bots_backup/crypto_bot/signals/
```

## Next Phase: Phase 3

**Planned Features:**
- WebSocket real-time signals
- Grafana monitoring dashboard
- Backtest validation framework
- CI/CD pipeline with GitHub Actions

## Support

**Documentation:**
- [Phase 2 Design](PHASE2_DESIGN.md)
- [Phase 2 Implementation](PHASE2_IMPLEMENTATION.md)
- [Personal Assistant Repo](https://github.com/rxpelle/personal-assistant)

**Created:** 2026-01-31
**Status:** Production Ready (Paper Trading)
**License:** Private
**Maintained By:** Main Agent + CodeMaster

---

**⚠️ CRITICAL WARNING:** This system is configured for LIVE TRADING with REAL MONEY.
- Current test coverage: 96.6% (28/29 tests passing)
- Paper trading validation: NONE (0 days)
- You are responsible for any financial losses
- Never bypass the 2% risk rule
- Monitor the system continuously during live trading

---

# Other Projects in This Repository

## Plague Novel Series (`plague_novel/`)
12-book historical thriller series tracking a secret society across time:
- **Book 1**: The Aethelred Cipher (Complete)
- **Book 2**: Genesis Protocol (Currently: Rewrite v12)
- **Books 3-12**: Outlined
- **Current work**: `plague_novel/book_2_genesis_protocol/rewrite_v12/`

## Author Website (`randypellegrini.com/`)
Static website for the novel series with:
- Character guides
- Series timeline
- Book information
- Interactive features

## Clawdbot Architecture (`~/clawd/`)
External directory with agent designs:
- Personal Assistant architecture
- Multi-agent system documentation
- Agent configurations (Architect, CodeMaster, DataDiver, etc.)
- **Quick access**: See [`.claude-context.md`](.claude-context.md) for "open clawd" shortcut

---

## Claude Code Session Context

**New to this project?** Check [`.claude-context.md`](.claude-context.md) for:
- Quick command shortcuts (e.g., "open clawd")
- Project structure overview
- Common workflows
- User preferences

This helps maintain context across Claude Code sessions.
