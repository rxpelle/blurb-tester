"""KENP report extractor — hits kdpreports.amazon.com backend directly."""

import csv
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .client import build_client

REPORTS_HOST = "kdpreports.amazon.com"

MARKETPLACE_CODES = {
    "ATVPDKIKX0DER": "US",
    "A1F83G8C2ARO7P": "UK",
    "A1PA6795UKMFR9": "DE",
    "A13V1IB3VIYZZH": "FR",
    "APJ6JRA9NG5V4": "IT",
    "A1RKKUPIHCS9HS": "ES",
    "A2EUQ1WTGCTBG2": "CA",
    "A1VC38T7YXB528": "JP",
    "A39IBJ37TRP1C6": "AU",
    "A2Q3Y263D00KWC": "BR",
    "A21TJRUUN4KGV": "IN",
    "A1AM78C64UM0Y8": "MX",
    "A19VAU5U5O7RUS": "SG",
    "ARBP9OOSHTCHU": "EG",
    "A17E79C6D8DWNP": "SA",
    "A1805IZSGTT6HS": "NL",
    "A1C3SOZRARQ6R3": "PL",
    "A33AVAJ2PDY3EV": "TR",
    "A2NODRKZP88ZB9": "SE",
}


def _fetch_csrf_token(client) -> str:
    r = client.get("/")
    m = re.search(r'"csrftoken":\s*\{\s*"token":\s*"([^"]+)"', r.text)
    if not m:
        raise RuntimeError("CSRF token not found in bootstrap HTML")
    return m.group(1)


def fetch_at_a_glance() -> dict:
    """GET /api/v2/reports/atAGlance — 22-day rolling snapshot per title."""
    client = build_client(host=REPORTS_HOST)
    try:
        csrf = _fetch_csrf_token(client)
        r = client.get(
            "/api/v2/reports/atAGlance",
            headers={"X-Csrf-Token": csrf},
        )
        r.raise_for_status()
        return r.json()
    finally:
        client.close()


def fetch_books_metadata() -> dict:
    """GET /metadata/reports/reportsMetadata — titles, digital/print ASIN pairs."""
    client = build_client(host=REPORTS_HOST)
    try:
        csrf = _fetch_csrf_token(client)
        r = client.get(
            "/metadata/reports/reportsMetadata",
            headers={"X-Csrf-Token": csrf},
        )
        r.raise_for_status()
        return r.json()
    finally:
        client.close()


def _build_asin_map(metadata: dict) -> dict[str, dict]:
    """Map ANY book ASIN (digital or print) -> {digital, print, title}."""
    books = metadata.get("reportsMetadata", {}).get("books", {})
    out: dict[str, dict] = {}
    for book in books.values():
        asins = book.get("asins", {})
        digital = asins.get("digital")
        print_ = asins.get("print")
        record = {
            "digital": digital,
            "print": print_,
            "title": book.get("titleName", ""),
        }
        for a in (digital, print_):
            if a:
                out[a] = record
    return out


def to_kenp_rows(payload: dict, asin_map: dict[str, dict]) -> list[dict]:
    """Flatten the atAGlance 'reads' section into rows keyed by canonical digital ASIN.

    The netUnits array is most-recent-first: index 0 = today.
    Only non-zero read days are emitted.
    """
    today = datetime.now(UTC).date()
    rows: list[dict] = []
    for entry in payload.get("records", {}).get("reads", []):
        title_id = entry.get("titleId", "")
        candidates = [a for a in title_id.split("|") if a]
        record = next((asin_map[a] for a in candidates if a in asin_map), None)
        if record:
            asin = record["digital"]
            title = record["title"]
        else:
            asin = candidates[0] if candidates else title_id
            title = ""
        mp_id = entry.get("marketplaceId", "")
        marketplace = MARKETPLACE_CODES.get(mp_id, mp_id)
        for offset, reads in enumerate(entry.get("netUnits", [])):
            if reads <= 0:
                continue
            rows.append({
                "asin": asin,
                "title": title,
                "date": (today - timedelta(days=offset)).isoformat(),
                "kenp_reads": reads,
                "marketplace": marketplace,
            })
    rows.sort(key=lambda r: (r["asin"], r["date"]))
    return rows


def write_csv(rows: list[dict], path: Path, asin_filter: str | None = None) -> int:
    """Write ku_page_flip-compatible CSV: date, kenp_reads, marketplace.

    If asin_filter is given, only rows matching that ASIN are written.
    """
    filtered = [r for r in rows if asin_filter is None or r["asin"] == asin_filter]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "kenp_reads", "marketplace"])
        for r in filtered:
            w.writerow([r["date"], r["kenp_reads"], r["marketplace"]])
    return len(filtered)


def export_all_asins(output_dir: Path, import_to_kupf: bool = False) -> dict[str, dict]:
    """Fetch from KDP and write one CSV per canonical digital ASIN.

    If import_to_kupf is True, also upserts rows into ku_page_flip's SQLite DB
    (idempotent via its UNIQUE(book_id, date, marketplace) constraint).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = fetch_books_metadata()
    asin_map = _build_asin_map(metadata)
    payload = fetch_at_a_glance()
    rows = to_kenp_rows(payload, asin_map)

    by_asin: dict[str, list[dict]] = {}
    titles: dict[str, str] = {}
    for r in rows:
        by_asin.setdefault(r["asin"], []).append(r)
        if r["title"]:
            titles[r["asin"]] = r["title"]

    result = {}
    for asin, asin_rows in by_asin.items():
        path = output_dir / f"kenp_{asin}.csv"
        count = write_csv(asin_rows, path, asin_filter=asin)
        entry = {
            "path": str(path),
            "rows": count,
            "title": titles.get(asin, ""),
        }
        if import_to_kupf:
            entry["imported"] = _import_to_ku_page_flip(
                asin=asin,
                title=titles.get(asin, asin),
                rows=asin_rows,
            )
        result[asin] = entry
    return result


def _import_to_ku_page_flip(asin: str, title: str, rows: list[dict]) -> int:
    """Upsert rows into ku_page_flip's DB. Returns count imported."""
    from datetime import date as _date

    from ku_page_flip.db import Database  # local import — optional dep

    with Database() as db:
        book = db.get_book_by_asin(asin) or db.add_book(title=title, asin=asin)
        for r in rows:
            db.add_daily_read(
                book_id=book.id,
                dt=_date.fromisoformat(r["date"]),
                kenp_reads=r["kenp_reads"],
                marketplace=r["marketplace"],
            )
    return len(rows)
