"""Kobo Writing Life CSV parser.

Expected columns:
  Date, Title, ISBN, Currency, Royalty, Units, Country
"""
import csv
import hashlib
import logging
from io import StringIO
from typing import List

from . import ParseError

logger = logging.getLogger(__name__)


def _find_column(headers: List[str], candidates: List[str]) -> int:
    headers_lower = [h.lower().strip() for h in headers]
    for candidate in candidates:
        cl = candidate.lower()
        for i, h in enumerate(headers_lower):
            if h == cl:
                return i
    for candidate in candidates:
        cl = candidate.lower()
        for i, h in enumerate(headers_lower):
            if cl in h:
                return i
    return -1


def _safe_float(val: str) -> float:
    try:
        return float(val.strip().replace(',', '').replace('$', ''))
    except (ValueError, AttributeError):
        return 0.0


def _safe_int(val: str) -> int:
    try:
        return int(val.strip().replace(',', ''))
    except (ValueError, AttributeError):
        return 0


def _row_hash(date: str, platform: str, fmt: str, marketplace: str) -> str:
    key = f"{date}|{platform}|{fmt}|{marketplace}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


def parse(filepath: str, book_id: int = None) -> List[dict]:
    """Parse a Kobo Writing Life royalty CSV."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    reader = csv.reader(StringIO(content))
    rows = list(reader)

    if not rows:
        raise ParseError('Empty CSV file')

    headers = rows[0]

    date_col = _find_column(headers, ['date', 'transaction date', 'sale date'])
    title_col = _find_column(headers, ['title', 'book title'])
    isbn_col = _find_column(headers, ['isbn', 'isbn-13'])
    currency_col = _find_column(headers, ['currency'])
    royalty_col = _find_column(headers, ['royalty', 'author revenue', 'earnings'])
    units_col = _find_column(headers, ['units', 'quantity', 'units sold'])
    country_col = _find_column(headers, ['country', 'territory', 'marketplace'])

    if date_col == -1:
        raise ParseError(f'Could not find date column in Kobo CSV. Headers: {headers}')
    if royalty_col == -1:
        raise ParseError(f'Could not find royalty column in Kobo CSV. Headers: {headers}')

    sales = []
    for row_num, row in enumerate(rows[1:], start=2):
        if not row or all(cell.strip() == '' for cell in row):
            continue

        try:
            date = row[date_col].strip() if date_col < len(row) else ''
            if not date:
                continue

            units = _safe_int(row[units_col]) if units_col >= 0 and units_col < len(row) else 0
            royalty = _safe_float(row[royalty_col]) if royalty_col < len(row) else 0.0
            currency = row[currency_col].strip() if currency_col >= 0 and currency_col < len(row) else 'USD'
            currency = currency or 'USD'
            country = row[country_col].strip() if country_col >= 0 and country_col < len(row) else ''

            is_refund = units < 0 or royalty < 0
            refund_amount = abs(royalty) if is_refund else 0.0
            royalty_amount = 0.0 if is_refund else royalty

            sale = {
                'book_id': book_id,
                'date': date,
                'units': abs(units),
                'royalty_amount': royalty_amount,
                'currency': currency,
                'format': 'ebook',
                'marketplace': country,
                'platform': 'kobo',
                'refund_amount': refund_amount,
                'tax_withheld': 0.0,
                'royalty_rate': None,
                'row_hash': _row_hash(date, 'kobo', 'ebook', country),
            }
            sales.append(sale)

        except Exception as e:
            logger.warning(f'Skipping row {row_num}: {e}')
            continue

    logger.info(f'Parsed {len(sales)} records from Kobo CSV: {filepath}')
    return sales
