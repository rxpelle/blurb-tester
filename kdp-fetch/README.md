# kdp-fetch

Headless backend client for KDP author reports. **No browser at runtime.**

Works by hitting `kdpreports.amazon.com` the same way KDP's own SPA does —
authenticated JSON endpoints behind a CSRF-protected session.

## Architecture

1. **Harvest** (infrequent, ~monthly when session expires): launches Chrome
   headless against a *copy* of the `playwright-persist` profile, exports
   cookies via CDP, writes to `~/.kdp-fetch/auth.json`. ~3 seconds.
2. **Fetch** (daily/on-demand): pure httpx. Reads cookies from JSON,
   pulls CSRF token from bootstrap HTML, calls `/api/v2/reports/*` endpoints.

After the harvest the browser is never touched. Fully cron-friendly.

## Endpoints discovered

Mined from the KDP SPA bundle at `dm2d4aq3e82uc.cloudfront.net/KDPReports.*.js`:

| Path | Use |
|---|---|
| `/api/v2/reports/atAGlance` | 22-day rolling snapshot: sales + KENP reads per title per marketplace |
| `/metadata/reports/reportsMetadata` | Book titles, digital/print ASIN pairs |
| `/api/v2/reports/customerMetadata` | Vendor code, account marketplace |
| `/api/v2/reports/customerPreferences` | Currency + royalty rate |
| `/download/report/kenpread/{id}/kenpReadReport.xslx` | Native XLSX download (not yet wired) |

## Usage

```bash
# One-time (and whenever session expires):
kdp-fetch harvest

# Confirm session is live:
kdp-fetch probe

# Export KENP CSVs (last 22 days, one file per digital ASIN)
# and upsert straight into ku_page_flip's SQLite DB:
kdp-fetch kenp --out ~/kdp-reports --import

# Export sales + royalty amounts as royalty_reconciler-compatible CSVs:
kdp-fetch royalties --out ~/kdp-reports

# Historical backfill — point at an XLSX manually downloaded from KDP Reports:
kdp-fetch backfill ~/Downloads/kenpReadReport.xslx

# Pipe into the analytics MCP:
# analytics_kenp_import(csv_path=~/kdp-reports/kenp_B0GPM973N1.csv, asin=B0GPM973N1)
# analytics_kenp_analyze(asin=B0GPM973N1)
```

Output CSV schema matches `ku_page_flip`: `date, kenp_reads, marketplace`.

## Daily ingest (cron)

`cron/daily_kenp.sh` runs `kenp --import` + `royalties` back-to-back against
a single harvested session. Installed at 9:30am local in crontab. Idempotent
— ku_page_flip's DB uses `INSERT OR REPLACE` on `(book_id, date, marketplace)`.

Logs: `/tmp/kdp-fetch-daily.log`. When it fails with a session-expired message,
run `kdp-fetch harvest` to refresh cookies (~3 seconds).
