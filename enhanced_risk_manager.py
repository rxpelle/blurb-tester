"""
Enhanced Risk Management Module with Alert Integration

Implements:
1. Kelly Criterion for optimal position sizing
2. Portfolio-level drawdown protection with alerts
3. Dynamic stop-loss based on volatility
4. Correlation-aware position limits
5. Performance tracking for Kelly calculations
6. Emergency alerting for critical events
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import DB_PATH, get_trades
from config import Config
import json
import os

# Import alerts with fallback
try:
    from alerts import send_emergency_stop_alert, send_data_error_alert, send_recovery_alert
    ALERTS_AVAILABLE = True
except ImportError:
    ALERTS_AVAILABLE = False
    print("[RISK] Alerts module not available")

RISK_STATE_FILE = os.path.join(os.path.dirname(__file__), 'risk_state.json')

class RiskManager:
    """Advanced risk management system with emergency alerting."""

    def __init__(self, initial_capital=None):
        self.initial_capital = initial_capital or Config.INITIAL_CAPITAL_USD
        self.max_portfolio_drawdown = 0.40  # 40% max drawdown (very aggressive - prevents premature shutdowns)
        self.drawdown_reduction_threshold = 0.25  # Reduce size at 25% (more aggressive)
        self.max_correlation_exposure = 0.80  # Max 80% in correlated assets (more aggressive)
        self.kelly_fraction = 0.35  # Use 35% of full Kelly (more aggressive)

        # Track suspicious equity drops
        self.last_equity = None
        self.equity_drop_threshold = 0.50  # Alert if equity drops >50% suddenly

        # Load or initialize state
        self.state = self._load_state()

    def _load_state(self):
        """Load risk manager state."""
        if os.path.exists(RISK_STATE_FILE):
            try:
                with open(RISK_STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass

        return {
            'peak_equity': self.initial_capital,
            'trading_enabled': True,
            'position_size_multiplier': 1.0,
            'last_updated': datetime.now().isoformat(),
            'alert_sent': False  # Track if emergency alert was sent
        }

    def _save_state(self):
        """Save risk manager state."""
        self.state['last_updated'] = datetime.now().isoformat()
        with open(RISK_STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _detect_data_anomaly(self, current_equity):
        """Detect suspicious equity drops that might be data errors."""
        if self.last_equity is None:
            self.last_equity = current_equity
            return False

        if current_equity <= 0:
            return True  # Zero or negative equity is definitely an error

        # Calculate drop percentage
        drop_pct = (self.last_equity - current_equity) / self.last_equity

        # If equity drops >50% in one check, it's likely a data error
        if drop_pct > self.equity_drop_threshold:
            if ALERTS_AVAILABLE:
                send_data_error_alert(
                    f"Equity dropped {drop_pct:.1%} in one cycle (${self.last_equity:.2f} → ${current_equity:.2f})",
                    affected_service="Exchange API"
                )
            return True

        self.last_equity = current_equity
        return False

    def calculate_kelly_criterion(self, symbol, lookback_days=30):
        """
        Calculate Kelly Criterion position size.

        Kelly % = (Win Rate * Avg Win - (1 - Win Rate) * Avg Loss) / Avg Win

        Returns: Recommended position size as fraction of equity (0.0 - 1.0)
        """
        trades = get_trades(symbol=symbol, days=lookback_days, limit=1000)

        if len(trades) < 10:
            # Not enough data, use conservative default
            print(f"[KELLY] Insufficient trade history for {symbol}, using default 5%")
            return 0.05

        # Calculate wins and losses
        wins = []
        losses = []

        # Group trades into round trips (buy -> sell pairs)
        buys = [t for t in trades if t['side'] == 'buy']
        sells = [t for t in trades if t['side'] == 'sell']

        # Match sells to buys (simplified - assumes FIFO)
        for i in range(min(len(buys), len(sells))):
            buy = buys[i]
            sell = sells[i]
            pnl_pct = (sell['price'] - buy['price']) / buy['price']

            if pnl_pct > 0:
                wins.append(pnl_pct)
            else:
                losses.append(abs(pnl_pct))

        if not wins or not losses:
            print(f"[KELLY] No complete win/loss pairs for {symbol}, using default 5%")
            return 0.05

        win_rate = len(wins) / (len(wins) + len(losses))
        avg_win = np.mean(wins)
        avg_loss = np.mean(losses)

        # Kelly Formula
        if avg_win == 0:
            kelly = 0.05
        else:
            kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win

        # Apply fractional Kelly for safety
        kelly_fractional = kelly * self.kelly_fraction

        # Cap between 0% and 20% (never risk more than 20% on single trade)
        kelly_capped = max(0.01, min(0.20, kelly_fractional))

        print(f"[KELLY] {symbol}: Win Rate={win_rate:.1%}, Avg Win={avg_win:.2%}, "
              f"Avg Loss={avg_loss:.2%}, Kelly={kelly:.2%}, "
              f"Fractional Kelly={kelly_capped:.2%}")

        return kelly_capped

    def check_portfolio_drawdown(self, current_equity):
        """
        Check portfolio drawdown and adjust trading if needed.
        Now includes data anomaly detection and alerting.

        Returns: (trading_enabled, position_multiplier)
        """
        # Detect data anomalies
        is_anomaly = self._detect_data_anomaly(current_equity)

        # Update peak equity
        if current_equity > self.state['peak_equity']:
            self.state['peak_equity'] = current_equity
            self.state['position_size_multiplier'] = 1.0
            self.state['trading_enabled'] = True
            self.state['alert_sent'] = False  # Reset alert flag

        # Calculate current drawdown
        drawdown = (self.state['peak_equity'] - current_equity) / self.state['peak_equity']

        # Check thresholds
        if drawdown >= self.max_portfolio_drawdown:
            # STOP TRADING - exceeded max drawdown
            if self.state['trading_enabled']:
                print(f"\n{'='*60}")
                print(f"⛔ PORTFOLIO DRAWDOWN PROTECTION TRIGGERED!")
                print(f"Current Drawdown: {drawdown:.1%} (Max: {self.max_portfolio_drawdown:.1%})")
                print(f"Peak Equity: ${self.state['peak_equity']:.2f}")
                print(f"Current Equity: ${current_equity:.2f}")
                print(f"Trading DISABLED until manual review")
                print(f"{'='*60}\n")

                # Send emergency alert (only once)
                if ALERTS_AVAILABLE and not self.state.get('alert_sent', False):
                    reason = "Drawdown limit exceeded"
                    if is_anomaly:
                        reason += " (possible data error detected)"

                    send_emergency_stop_alert(
                        drawdown_pct=drawdown * 100,
                        peak_equity=self.state['peak_equity'],
                        current_equity=current_equity,
                        reason=reason
                    )
                    self.state['alert_sent'] = True

                self.state['trading_enabled'] = False
                self.state['position_size_multiplier'] = 0.0

        elif drawdown >= self.drawdown_reduction_threshold:
            # Reduce position sizes
            multiplier = 1.0 - (drawdown / self.max_portfolio_drawdown) * 0.5
            multiplier = max(0.25, multiplier)  # Never go below 25%

            if abs(self.state['position_size_multiplier'] - multiplier) > 0.05:
                print(f"\n[RISK] Drawdown Protection: Reducing position sizes to {multiplier:.0%}")
                print(f"[RISK] Current Drawdown: {drawdown:.1%} (Threshold: {self.drawdown_reduction_threshold:.1%})")

            self.state['position_size_multiplier'] = multiplier
            self.state['trading_enabled'] = True
        else:
            # Normal trading
            self.state['position_size_multiplier'] = 1.0
            self.state['trading_enabled'] = True

        self._save_state()

        return self.state['trading_enabled'], self.state['position_size_multiplier']

    def calculate_dynamic_stop_loss(self, df, multiplier=2.0, min_stop_pct=0.01, max_stop_pct=0.05):
        """
        Calculate dynamic stop loss based on ATR (volatility).

        In high volatility: wider stops
        In low volatility: tighter stops

        Returns: stop_loss_distance (in price units)
        """
        if df.empty or len(df) < 14:
            # Fallback to fixed percentage
            return df.iloc[-1]['close'] * 0.02

        # Calculate ATR
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)

        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()

        current_atr = atr.iloc[-1]
        current_price = df.iloc[-1]['close']

        if pd.isna(current_atr):
            return current_price * 0.02

        # Stop distance = ATR * multiplier
        stop_distance = current_atr * multiplier

        # Convert to percentage
        stop_pct = stop_distance / current_price

        # Cap between min and max
        stop_pct_capped = max(min_stop_pct, min(max_stop_pct, stop_pct))

        stop_distance_final = current_price * stop_pct_capped

        print(f"[RISK] Dynamic Stop: ATR=${current_atr:.2f}, "
              f"Stop Distance=${stop_distance_final:.2f} ({stop_pct_capped:.1%})")

        return stop_distance_final

    def calculate_position_size_with_kelly(self, symbol, total_equity, atr_stop_distance,
                                          current_price, base_risk_pct=0.05):
        """
        Calculate optimal position size using Kelly Criterion + Risk Management.

        Steps:
        1. Get Kelly recommendation
        2. Apply portfolio drawdown multiplier
        3. Calculate shares based on stop distance
        4. Apply safety caps

        Returns: position_size (in units of asset)
        """
        # 1. Kelly Criterion
        kelly_pct = self.calculate_kelly_criterion(symbol)

        # 2. Check drawdown protection
        trading_enabled, drawdown_multiplier = self.check_portfolio_drawdown(total_equity)

        if not trading_enabled:
            print(f"[RISK] Trading disabled due to drawdown protection")
            return 0.0

        # 3. Calculate position size
        # Method: Risk-based sizing with Kelly
        # Risk Amount = Total Equity * Kelly% * Drawdown Multiplier
        risk_amount = total_equity * kelly_pct * drawdown_multiplier

        # Position Size = Risk Amount / Stop Distance
        if atr_stop_distance and atr_stop_distance > 0:
            position_size = risk_amount / atr_stop_distance
        else:
            # Fallback: use 2% stop
            fallback_stop = current_price * 0.02
            position_size = risk_amount / fallback_stop

        # 4. Safety caps
        max_position_value = total_equity * 0.25  # Never more than 25% of equity in one position
        max_position_size = max_position_value / current_price

        position_size_final = min(position_size, max_position_size)

        print(f"[RISK] Position Sizing:")
        print(f"  Kelly: {kelly_pct:.1%} | Drawdown Multiplier: {drawdown_multiplier:.1%}")
        print(f"  Risk Amount: ${risk_amount:.2f}")
        print(f"  Position Size: {position_size_final:.6f} (${position_size_final * current_price:.2f})")

        return position_size_final

    def check_correlation_limit(self, symbols_with_positions, new_symbol):
        """
        Check if adding new_symbol would violate correlation limits.

        High correlation pairs (>0.7):
        - BTC/ETH (0.85+)
        - BTC/SOL (0.75+)
        - Memecoins: DOGE/PEPE/WIF (0.80+)

        Returns: (allowed, reason)
        """
        # Correlation matrix (simplified - you could calculate dynamically)
        correlations = {
            ('BTC/USD', 'ETH/USD'): 0.85,
            ('BTC/USD', 'SOL/USD'): 0.75,
            ('ETH/USD', 'SOL/USD'): 0.70,
            ('DOGE/USD', 'PEPE/USD'): 0.80,
            ('DOGE/USD', 'WIF/USD'): 0.75,
            ('PEPE/USD', 'WIF/USD'): 0.85,
        }

        # Count highly correlated positions
        correlated_count = 0
        total_positions = len(symbols_with_positions)

        for existing in symbols_with_positions:
            pair = tuple(sorted([existing, new_symbol]))
            correlation = correlations.get(pair, 0.0)

            if correlation >= 0.70:
                correlated_count += 1

        # Calculate correlation exposure
        if total_positions > 0:
            correlation_exposure = correlated_count / total_positions
        else:
            correlation_exposure = 0.0

        # Check limit
        if correlation_exposure > self.max_correlation_exposure:
            return False, f"Correlation exposure too high ({correlation_exposure:.0%} > {self.max_correlation_exposure:.0%})"

        return True, "OK"

    def get_risk_report(self, total_equity):
        """Generate risk management report."""
        drawdown = (self.state['peak_equity'] - total_equity) / self.state['peak_equity']

        return {
            'peak_equity': self.state['peak_equity'],
            'current_equity': total_equity,
            'drawdown': drawdown,
            'drawdown_pct': drawdown * 100,
            'trading_enabled': self.state['trading_enabled'],
            'position_multiplier': self.state['position_size_multiplier'],
            'status': 'NORMAL' if drawdown < 0.10 else 'REDUCED' if drawdown < 0.15 else 'STOPPED'
        }


# Singleton instance
_risk_manager = None

def get_risk_manager(initial_capital=None):
    """Get or create risk manager singleton."""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager(initial_capital)
    return _risk_manager


if __name__ == "__main__":
    # Test Kelly calculation
    rm = RiskManager(initial_capital=6000)

    print("\n=== Risk Manager Test ===\n")

    # Test Kelly
    kelly = rm.calculate_kelly_criterion('BTC/USD', lookback_days=30)
    print(f"\nKelly Criterion: {kelly:.2%}\n")

    # Test drawdown protection
    print("Testing Drawdown Protection:")
    test_equities = [6000, 5500, 5100, 4800]
    for equity in test_equities:
        enabled, multiplier = rm.check_portfolio_drawdown(equity)
        print(f"Equity ${equity}: Enabled={enabled}, Multiplier={multiplier:.1%}")
