"""Royalty report extractor — reuses atAGlance payload for sales + royalty amounts.

The atAGlance endpoint returns a 22-day rolling window with three parallel
record types (sales, reads, royalties), each an array of per-day values
indexed most-recent-first (index 0 = today).

Royalty amounts are pre-converted to the account currency
(kdpCustomerPreferences.royaltiesEstimatorSettings.currency — typically USD).

Output CSV matches the format expected by royalty_reconciler's KDP parser:
  Date, Title, ASIN, Marketplace, Format, Units Sold, Royalty, Currency
"""

import csv
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .kenp import MARKETPLACE_CODES, _build_asin_map, fetch_at_a_glance, fetch_books_metadata


def to_royalty_rows(payload: dict, asin_map: dict[str, dict]) -> list[dict]:
    """Flatten atAGlance sales+royalties into one row per (date, book, marketplace, format).

    Correlates sales and royalty arrays by (titleId, marketplaceId, channelId).
    Emits a row whenever units>0 OR royalty>0 on a given day.
    """
    today = datetime.now(UTC).date()
    currency = (
        payload.get("kdpCustomerPreferences", {})
        .get("royaltiesEstimatorSettings", {})
        .get("currency", "USD")
    )
    records = payload.get("records", {})

    # Index royalties by (titleId, marketplaceId, channelId) -> amount array.
    royalty_idx: dict[tuple, list[float]] = {}
    for r in records.get("royalties", []):
        key = (r.get("titleId", ""), r.get("marketplaceId", ""), r.get("channelId", ""))
        royalty_idx[key] = r.get("amount", [])

    # Track which royalty keys we've already emitted so we don't double-count
    # the royalty-only days when walking sales.
    seen_keys: set[tuple] = set()

    rows: list[dict] = []

    def _resolve(title_id: str) -> tuple[str, str]:
        candidates = [a for a in title_id.split("|") if a]
        rec = next((asin_map[a] for a in candidates if a in asin_map), None)
        if rec:
            return rec["digital"] or rec["print"] or candidates[0], rec["title"]
        return (candidates[0] if candidates else title_id), ""

    for s in records.get("sales", []):
        title_id = s.get("titleId", "")
        mp_id = s.get("marketplaceId", "")
        channel = s.get("channelId", "")
        key = (title_id, mp_id, channel)
        seen_keys.add(key)

        asin, title = _resolve(title_id)
        marketplace = MARKETPLACE_CODES.get(mp_id, mp_id)
        fmt = "kindle" if channel == "kindle" else "paperback" if channel == "print" else channel
        amounts = royalty_idx.get(key, [])

        for offset, units in enumerate(s.get("netUnits", [])):
            royalty = amounts[offset] if offset < len(amounts) else 0.0
            if units <= 0 and royalty <= 0:
                continue
            rows.append({
                "date": (today - timedelta(days=offset)).isoformat(),
                "title": title,
                "asin": asin,
                "marketplace": marketplace,
                "format": fmt,
                "units": units,
                "royalty": round(royalty, 4),
                "currency": currency,
            })

    # Emit royalty-only rows (KU read-through revenue shows up here without a sale).
    for (title_id, mp_id, channel), amounts in royalty_idx.items():
        if (title_id, mp_id, channel) in seen_keys:
            continue
        asin, title = _resolve(title_id)
        marketplace = MARKETPLACE_CODES.get(mp_id, mp_id)
        fmt = "kindle" if channel == "kindle" else "paperback" if channel == "print" else channel
        for offset, royalty in enumerate(amounts):
            if royalty <= 0:
                continue
            rows.append({
                "date": (today - timedelta(days=offset)).isoformat(),
                "title": title,
                "asin": asin,
                "marketplace": marketplace,
                "format": fmt,
                "units": 0,
                "royalty": round(royalty, 4),
                "currency": currency,
            })

    rows.sort(key=lambda r: (r["asin"], r["date"], r["marketplace"], r["format"]))
    return rows


COLUMNS = ["Date", "Title", "ASIN", "Marketplace", "Format", "Units Sold", "Royalty", "Currency"]


def write_csv(rows: list[dict], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([
                r["date"], r["title"], r["asin"], r["marketplace"],
                r["format"], r["units"], f"{r['royalty']:.4f}", r["currency"],
            ])
    return len(rows)


def export_royalties(output_dir: Path) -> dict[str, dict]:
    """Fetch royalties from KDP, write one CSV per canonical digital ASIN + one combined."""
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = fetch_books_metadata()
    asin_map = _build_asin_map(metadata)
    payload = fetch_at_a_glance()
    rows = to_royalty_rows(payload, asin_map)

    by_asin: dict[str, list[dict]] = defaultdict(list)
    titles: dict[str, str] = {}
    for r in rows:
        by_asin[r["asin"]].append(r)
        if r["title"]:
            titles[r["asin"]] = r["title"]

    result: dict[str, dict] = {}
    for asin, asin_rows in by_asin.items():
        path = output_dir / f"royalties_{asin}.csv"
        count = write_csv(asin_rows, path)
        result[asin] = {
            "path": str(path),
            "rows": count,
            "title": titles.get(asin, ""),
            "total_royalty": round(sum(r["royalty"] for r in asin_rows), 2),
            "total_units": sum(r["units"] for r in asin_rows),
        }

    if rows:
        combined = output_dir / "royalties_all.csv"
        write_csv(rows, combined)
        result["_combined"] = {
            "path": str(combined),
            "rows": len(rows),
            "total_royalty": round(sum(r["royalty"] for r in rows), 2),
        }

    return result
