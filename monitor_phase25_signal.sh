#!/bin/bash
# Phase 2.5 Signal Monitor
# Watches for new signals with Phase 2.5 enhancements

echo "=================================================="
echo "Phase 2.5 Signal Monitor"
echo "=================================================="
echo "Watching for new signals with:"
echo "  ✓ ML predictions"
echo "  ✓ Market regime detection"
echo "  ✓ Multi-timeframe filtering"
echo "  ✓ Volume confirmation"
echo ""
echo "Next signal expected around: $(date -v+7M '+%H:%M:%S')"
echo "Press Ctrl+C to stop monitoring"
echo "=================================================="
echo ""

# Get the ID of the most recent signal
LAST_SIGNAL_ID=$(curl -s "http://localhost:8788/api/trading/signals?limit=1" | jq -r '.signals[0].id // 0')
echo "Monitoring for signals newer than ID: $LAST_SIGNAL_ID"
echo ""

# Monitor loop
while true; do
    # Check for new signal
    LATEST=$(curl -s "http://localhost:8788/api/trading/signals?limit=1")
    LATEST_ID=$(echo "$LATEST" | jq -r '.signals[0].id // 0')

    if [ "$LATEST_ID" -gt "$LAST_SIGNAL_ID" ]; then
        # New signal detected!
        echo ""
        echo "🎉 NEW PHASE 2.5 SIGNAL DETECTED! 🎉"
        echo "=================================================="

        # Extract and display Phase 2.5 features
        echo "$LATEST" | jq -r '.signals[0] | "
Symbol: \(.symbol)
Signal: \(.signal)
Confidence: \(.confidence)%
Price: $\(.price_at_signal)

📊 SCORES:
  Technical: \(.technical_score // "N/A")
  ML Score: \(.ml_score // "N/A")
  Sentiment: \(.sentiment_score // "N/A")
  Volume: \(.volume_score // "N/A")

🤖 ML PREDICTIONS (Phase 2.5):
  Available: \(.ml_available // false)
  Prediction: \(.ml_prediction // "N/A")
  Confidence: \(.ml_confidence // 0)%

📈 MARKET REGIME (Phase 2.5):
  Type: \(.market_regime // "N/A")
  ADX: \(.adx // "N/A")

🔍 FILTERS (Phase 2.5):
  MTF Aligned: \(.mtf_aligned // "unknown")
  Volume Confirmed: \(.volume_confirmed // "unknown")
  Filters Passed: \(.filters.filters_passed // "unknown")

💭 REASONING:
"'

        # Show ML reasoning if available
        echo "$LATEST" | jq -r '.signals[0].reasoning.ml // "  ML: N/A"'
        echo "$LATEST" | jq -r '.signals[0].reasoning.regime // "  Regime: N/A"'
        echo "$LATEST" | jq -r '.signals[0].reasoning.mtf_filter // "  MTF: N/A"'
        echo "$LATEST" | jq -r '.signals[0].reasoning.volume_confirmation // "  Volume: N/A"'

        echo ""
        echo "=================================================="
        echo "✅ Phase 2.5 enhancements are ACTIVE!"
        echo ""

        # Play system sound (macOS)
        afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true

        # Update last signal ID
        LAST_SIGNAL_ID=$LATEST_ID

        echo "Continuing to monitor for next signal..."
        echo ""
    else
        # No new signal yet - show progress indicator
        printf "\r⏳ Waiting for next signal... (last check: $(date '+%H:%M:%S'))"
    fi

    # Check every 10 seconds
    sleep 10
done
