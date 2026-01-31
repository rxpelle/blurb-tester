# Balanced Aggressive Mode - Crypto Trading Bot

**Date Enabled**: 2026-01-17
**Previous Mode**: Full Aggressive
**Reason**: User requested dial-back for better risk control while maintaining aggressive posture

---

## Settings Comparison

| Parameter | Conservative | Full Aggressive | **Balanced Aggressive** |
|-----------|-------------|----------------|------------------------|
| Kelly Fraction | 35% | 50% | **40%** ✓ |
| Risk per Trade | 7% | 10% | **8%** ✓ |
| ML Confidence | 70% | 60% | **60%** |
| Stop Loss | 3% | 5% | **5%** |
| Pyramid Max | 2 | 3 | **3** |
| Pyramid Threshold | 2% | 1.5% | **1.5%** |

---

## Risk Impact Analysis

### Position Sizing (on $6,200 equity):
- **Full Aggressive**: Max $620/trade loss (10%), positions up to $3,100 (50% Kelly)
- **Balanced Aggressive**: Max $496/trade loss (8%), positions up to $2,480 (40% Kelly)
- **Difference**: $124 less risk per trade, $620 smaller position sizes

### Worst Case Scenarios:
**3 Losing Trades in a Row:**
- Full Aggressive: -30% ($1,860 loss) → Equity: $4,340
- Balanced Aggressive: -24% ($1,488 loss) → Equity: $4,712
- **Protection**: $372 better worst-case outcome

**5 Losing Trades in a Row:**
- Full Aggressive: -50% ($3,100 loss) → Equity: $3,100 (triggers emergency stop)
- Balanced Aggressive: -40% ($2,480 loss) → Equity: $3,720 (still trading)
- **Protection**: $620 better outcome, avoids emergency stop

---

## Expected Performance

### Advantages of Balanced Aggressive:
✅ Still 14% larger positions than conservative (40% vs 35% Kelly)
✅ Still 14% more risk per trade than conservative (8% vs 7%)
✅ Still takes more trades (60% ML confidence vs 70%)
✅ Better downside protection than full aggressive
✅ Less likely to trigger drawdown emergency stops
✅ More sustainable for long-term growth

### Trade-offs:
⚠️ Slightly smaller profits when trades work (20% smaller positions than full aggressive)
⚠️ Slower equity growth than full aggressive in bull markets

---

## Files Modified

1. **`/app/config.py`**
   - Changed `risk_pct: 0.10` → `0.08` for all trading pairs
   - Backup: `/app/config.py.backup.aggressive`

2. **`/app/risk_manager.py`**
   - Changed `kelly_fraction = 0.50` → `0.40`
   - Backup: `/app/risk_manager.py.backup.aggressive`

---

## Revert Instructions

### To Full Aggressive:
```bash
docker exec trading-bot cp /app/config.py.backup.aggressive /app/config.py
docker exec trading-bot cp /app/risk_manager.py.backup.aggressive /app/risk_manager.py
docker restart trading-bot
```

### To Conservative:
```bash
docker exec trading-bot sed -i "s/'risk_pct': 0.08/'risk_pct': 0.07/g" /app/config.py
docker exec trading-bot sed -i 's/self.kelly_fraction = 0.40/self.kelly_fraction = 0.35/g' /app/risk_manager.py
docker exec trading-bot sed -i 's/ML_CONFIDENCE_THRESHOLD = 0.60/ML_CONFIDENCE_THRESHOLD = 0.70/g' /app/config.py
docker exec trading-bot sed -i 's/STOP_LOSS_PCT = 0.05/STOP_LOSS_PCT = 0.03/g' /app/config.py
docker exec trading-bot sed -i 's/PYRAMID_MAX_ADDITIONS = 3/PYRAMID_MAX_ADDITIONS = 2/g' /app/config.py
docker exec trading-bot sed -i 's/PYRAMID_MIN_PROFIT_PCT = 0.015/PYRAMID_MIN_PROFIT_PCT = 0.02/g' /app/config.py
docker restart trading-bot
```

---

## Monitoring Recommendations

**Watch for:**
1. Win rate (should stay above 55%)
2. Average win vs average loss ratio (should be >1.5:1)
3. Maximum consecutive losses (alert if >3)
4. Drawdown from peak (alert if >15%)

**Telegram Alerts Active:**
- ✅ Emergency stop at 40% drawdown
- ✅ Data error detection
- ✅ Manual trading enable/disable notifications

---

## Status: ✅ ACTIVE

Bot restarted at 2026-01-17 with balanced aggressive settings.
Daily optimization running normally.
All 6 pairs active: BTC, ETH, SOL, PEPE, WIF, DOGE.
