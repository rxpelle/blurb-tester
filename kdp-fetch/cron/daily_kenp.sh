#!/bin/bash
# Daily KENP ingest: export last 22 days of reads from KDP, upsert into ku_page_flip DB.
# Idempotent — safe to re-run.

set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

LOG=/tmp/kdp-fetch-daily.log
OUT=/Users/randypellegrini/kdp-reports

{
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) daily KDP ingest ==="
  if ! kdp-fetch kenp --out "$OUT" --import; then
    echo "KENP FAILED — session may have expired. Run: kdp-fetch harvest"
    exit 1
  fi
  if ! kdp-fetch royalties --out "$OUT"; then
    echo "ROYALTIES FAILED — session may have expired. Run: kdp-fetch harvest"
    exit 1
  fi
} >> "$LOG" 2>&1
