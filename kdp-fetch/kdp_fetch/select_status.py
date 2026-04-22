"""KDP Select enrollment status extractor — hits kdp.amazon.com Bookshelf backend.

The Bookshelf is a server-rendered page (unlike kdpreports.amazon.com which is an SPA).
Each enrolled book has a per-title detail page at:
    /action/dualbookshelf.selectinfo/en_US/marketing/{titleId}/promotion-manager?showDetailsPopover=true

which redirects to /en_US/marketing/{titleId}/promotion-manager and contains the
"Term start date" / "Term end date" strings we need to parse.

titleId is KDP's internal asset ID (e.g. A2MBM4DEYKGIJQ), distinct from the Amazon ASIN.
We discover them by parsing the bookshelf HTML for the data-dual-bookshelf-action blobs.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from html import unescape

import httpx

from .client import DEFAULT_HEADERS, build_client

BOOKSHELF_HOST = "kdp.amazon.com"


@dataclass
class SelectEnrollment:
    title_id: str
    asin: str | None
    title: str | None
    status: str | None  # "Enrolled", "Not enrolled", etc.
    term_start: date | None
    term_end: date | None
    term_start_raw: str | None
    term_end_raw: str | None

    def days_until_end(self, today: date | None = None) -> int | None:
        if self.term_end is None:
            return None
        today = today or date.today()
        return (self.term_end - today).days


def _bookshelf_client() -> httpx.Client:
    """httpx client for kdp.amazon.com that follows redirects."""
    c = build_client(host=BOOKSHELF_HOST)
    # build_client returns follow_redirects=False; rewrap with True.
    follow = httpx.Client(
        base_url=c.base_url,
        headers={**DEFAULT_HEADERS, "Referer": f"https://{BOOKSHELF_HOST}/"},
        cookies=c.cookies,
        timeout=c.timeout,
        follow_redirects=True,
    )
    c.close()
    return follow


_ACTION_BLOB_RE = re.compile(
    r'data-(?:dual-bookshelf-action|link-parameters)="(\{(?:[^"\\]|\\.)*\})"'
)
_DATE_RE = re.compile(r"([A-Z][a-z]+ \d+,? \d{4})")


def _enrolled_title_ids_from_bookshelf(html: str) -> list[str]:
    """Extract unique titleIds of books currently ENROLLED in KDP Select."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for m in _ACTION_BLOB_RE.finditer(html):
        raw = unescape(m.group(1))
        try:
            blob = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if blob.get("select") != "ENROLLED":
            continue
        tid = blob.get("titleId")
        if tid and tid not in seen_set:
            seen_set.add(tid)
            seen.append(tid)
    return seen


def _parse_term_date(raw: str) -> date | None:
    """Parse 'April 27, 2026 PDT' or 'January 28, 2026 PST' to a date."""
    m = _DATE_RE.search(raw)
    if not m:
        return None
    for fmt in ("%B %d, %Y", "%B %d %Y"):
        try:
            return datetime.strptime(m.group(1), fmt).date()
        except ValueError:
            continue
    return None


def _parse_select_detail(html: str, title_id: str) -> SelectEnrollment:
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    status_m = re.search(r"Your Current KDP Select Status:\s*([A-Za-z ]+?)\s+Term", text)
    start_m = re.search(r"Term start date:\s*([A-Za-z]+ \d+,? \d{4}(?:\s+[A-Z]{2,3})?)", text)
    end_m = re.search(r"Term end date:\s*([A-Za-z]+ \d+,? \d{4}(?:\s+[A-Z]{2,3})?)", text)
    asin_m = re.search(r"B0[A-Z0-9]{8}", html)
    title_m = re.search(r"<title>(.*?)</title>", html)

    start_raw = start_m.group(1) if start_m else None
    end_raw = end_m.group(1) if end_m else None
    return SelectEnrollment(
        title_id=title_id,
        asin=asin_m.group(0) if asin_m else None,
        title=(title_m.group(1).strip() if title_m else None),
        status=(status_m.group(1).strip() if status_m else None),
        term_start=_parse_term_date(start_raw) if start_raw else None,
        term_end=_parse_term_date(end_raw) if end_raw else None,
        term_start_raw=start_raw,
        term_end_raw=end_raw,
    )


def fetch_enrollments() -> list[SelectEnrollment]:
    """Return one SelectEnrollment per KDP-Select-enrolled title on the bookshelf."""
    client = _bookshelf_client()
    try:
        shelf = client.get("/en_US/bookshelf")
        shelf.raise_for_status()
        title_ids = _enrolled_title_ids_from_bookshelf(shelf.text)
        results: list[SelectEnrollment] = []
        for tid in title_ids:
            r = client.get(
                f"/action/dualbookshelf.selectinfo/en_US/marketing/{tid}"
                "/promotion-manager?showDetailsPopover=true"
            )
            if r.status_code != 200:
                results.append(
                    SelectEnrollment(
                        title_id=tid, asin=None, title=None,
                        status=f"HTTP {r.status_code}", term_start=None, term_end=None,
                        term_start_raw=None, term_end_raw=None,
                    )
                )
                continue
            results.append(_parse_select_detail(r.text, tid))
        return results
    finally:
        client.close()


def enrich_with_titles(enrollments: list[SelectEnrollment]) -> list[SelectEnrollment]:
    """Replace the generic page <title> with the real book title from reportsMetadata."""
    from .kenp import fetch_books_metadata

    try:
        md = fetch_books_metadata()
    except Exception:
        return enrollments
    asin_to_title: dict[str, str] = {}
    for book in md.get("reportsMetadata", {}).get("books", {}).values():
        asins = book.get("asins") or {}
        name = book.get("titleName", "")
        for a in (asins.get("digital"), asins.get("print")):
            if a:
                asin_to_title[a] = name
    for e in enrollments:
        if e.asin and e.asin in asin_to_title:
            e.title = asin_to_title[e.asin]
    return enrollments
