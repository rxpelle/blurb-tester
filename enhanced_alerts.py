"""
Enhanced Telegram Alerting Module with Emergency Notifications

Sends notifications when trades are executed or important events occur.
Now includes emergency alerts for trading stops and data errors.

To set up:
1. Create a bot via @BotFather on Telegram
2. Get your chat ID by messaging @userinfobot
3. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env
"""

import os
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def is_configured():
    """Check if Telegram is configured."""
    return TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID

def send_alert(message, silent=False):
    """Send a message to Telegram."""
    if not is_configured():
        print(f"[TELEGRAM] Not configured - would have sent: {message[:100]}...")
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_notification': silent
        }
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"[TELEGRAM] Failed to send: {e}")
        return False

def send_trade_alert(side, amount, price, symbol="BTC/USD"):
    """Send trade execution alert."""
    emoji = "🟢" if side == 'buy' else "🔴"
    message = f"""
{emoji} *TRADE EXECUTED*
━━━━━━━━━━━━━━━
**{side.upper()}** {amount} {symbol.split('/')[0]}
**Price:** ${price:,.2f}
**Time:** {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━
"""
    return send_alert(message)

def send_stop_loss_alert(price, stop_price, pnl_pct):
    """Send stop loss triggered alert."""
    emoji = "⚠️" if pnl_pct < 0 else "🛑"
    message = f"""
{emoji} *STOP LOSS TRIGGERED*
━━━━━━━━━━━━━━━
**Price:** ${price:,.2f}
**Stop:** ${stop_price:,.2f}
**PnL:** {pnl_pct:+.2f}%
━━━━━━━━━━━━━━━
"""
    return send_alert(message)

def send_emergency_stop_alert(drawdown_pct, peak_equity, current_equity, reason="Drawdown limit exceeded"):
    """Send CRITICAL alert when trading is emergency stopped."""
    message = f"""
🚨 *EMERGENCY: TRADING STOPPED* 🚨
━━━━━━━━━━━━━━━
**Reason:** {reason}
**Drawdown:** {drawdown_pct:.1f}%
**Peak Equity:** ${peak_equity:,.2f}
**Current Equity:** ${current_equity:,.2f}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ *MANUAL REVIEW REQUIRED*
Bot will not resume trading automatically.
━━━━━━━━━━━━━━━
"""
    # Send with notification enabled (not silent)
    return send_alert(message, silent=False)

def send_data_error_alert(error_message, affected_service="Unknown"):
    """Send alert for critical data errors that might affect trading."""
    message = f"""
⚠️ *DATA ERROR DETECTED*
━━━━━━━━━━━━━━━
**Service:** {affected_service}
**Error:** {error_message}
**Time:** {datetime.now().strftime('%H:%M:%S')}

This may affect trading decisions.
Monitoring for recovery...
━━━━━━━━━━━━━━━
"""
    return send_alert(message, silent=False)

def send_recovery_alert(previous_equity, current_equity):
    """Send alert when equity recovers after an error."""
    message = f"""
✅ *EQUITY RECOVERED*
━━━━━━━━━━━━━━━
**Previous:** ${previous_equity:,.2f}
**Current:** ${current_equity:,.2f}
**Time:** {datetime.now().strftime('%H:%M:%S')}

Data error appears resolved.
Trading remains disabled pending review.
━━━━━━━━━━━━━━━
"""
    return send_alert(message, silent=True)

def send_daily_summary(total_trades, pnl, balance_usd, balance_btc, btc_price):
    """Send daily performance summary."""
    total_value = balance_usd + (balance_btc * btc_price)
    message = f"""
📊 *DAILY SUMMARY*
━━━━━━━━━━━━━━━
**Trades:** {total_trades}
**PnL:** ${pnl:+,.2f}
**USD:** ${balance_usd:,.2f}
**BTC:** {balance_btc:.6f}
**Total:** ${total_value:,.2f}
━━━━━━━━━━━━━━━
"""
    return send_alert(message)

def send_startup_alert():
    """Send bot startup notification."""
    message = f"""
🤖 *BOT STARTED*
━━━━━━━━━━━━━━━
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Strategy:** Enhanced v3.0
Bot is now monitoring...
━━━━━━━━━━━━━━━
"""
    return send_alert(message)

def send_trading_resumed_alert(current_equity):
    """Send alert when trading is manually re-enabled."""
    message = f"""
▶️ *TRADING RESUMED*
━━━━━━━━━━━━━━━
**Current Equity:** ${current_equity:,.2f}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Bot is actively trading again.
━━━━━━━━━━━━━━━
"""
    return send_alert(message, silent=False)
