# Aggressive Configuration Changes for Bitcoin Uptrend
# Apply these changes to make the bot more aggressive

"""
CHANGES TO MAKE:

1. Increase Kelly Fraction (risk_manager.py):
   - Current: 0.35 (35% of Kelly)
   - New: 0.50 (50% of Kelly) - More aggressive position sizing

2. Increase Position Size per Trade (config.py):
   - Current: 7% risk per trade
   - New: 10% risk per trade

3. Lower ML Confidence Threshold (config.py):
   - Current: 0.70 (70% confidence required)
   - New: 0.60 (60% confidence) - Take more trades

4. Wider Stop Loss (config.py):
   - Current: 3% stop loss
   - New: 5% stop loss - Give positions more room to breathe

5. More Aggressive Pyramid Settings (config.py):
   - Current: Max 2 additions, 2% profit required
   - New: Max 3 additions, 1.5% profit required - Add to winners faster
"""

# File 1: risk_manager.py changes
RISK_MANAGER_CHANGES = """
Line ~55: Change kelly_fraction
FROM: self.kelly_fraction = 0.35  # Use 35% of full Kelly (more aggressive)
TO:   self.kelly_fraction = 0.50  # Use 50% of full Kelly (VERY aggressive)
"""

# File 2: config.py changes
CONFIG_CHANGES = """
Line ~30: Change risk_pct for all trading pairs
FROM: 'risk_pct': 0.07  (7%)
TO:   'risk_pct': 0.10  (10%)

Line ~43: Change ML_CONFIDENCE_THRESHOLD
FROM: ML_CONFIDENCE_THRESHOLD = 0.70
TO:   ML_CONFIDENCE_THRESHOLD = 0.60

Line ~47: Change PYRAMID settings
FROM: PYRAMID_MAX_ADDITIONS = 2
      PYRAMID_MIN_PROFIT_PCT = 0.02
TO:   PYRAMID_MAX_ADDITIONS = 3
      PYRAMID_MIN_PROFIT_PCT = 0.015

Line ~25: Change STOP_LOSS_PCT
FROM: STOP_LOSS_PCT = 0.03  # 3%
TO:   STOP_LOSS_PCT = 0.05  # 5%
"""

print("=" * 70)
print("AGGRESSIVE MODE CONFIGURATION")
print("=" * 70)
print("\nThese changes will make your bot:")
print("  ✓ Take 50% larger positions (Kelly 50% vs 35%)")
print("  ✓ Risk 10% per trade (vs 7%)")
print("  ✓ Accept trades with 60% confidence (vs 70%)")
print("  ✓ Use 5% stop losses (vs 3%) - more room")
print("  ✓ Pyramid into winners faster (1.5% vs 2%)")
print("  ✓ Add up to 3x to winning positions (vs 2x)")
print("\n⚠️  WARNING: Higher potential returns = Higher risk")
print("=" * 70)
