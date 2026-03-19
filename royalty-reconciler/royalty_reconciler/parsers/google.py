"""Google Play Books CSV parser.

Expected columns:
  Transaction Date, Title, Quantity, Earnings, Currency
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
    """Parse a Google Play Books earnings CSV."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    reader = csv.reader(StringIO(content))
    rows = list(reader)

    if not rows:
        raise ParseError('Empty CSV file')

    headers = rows[0]

    date_col = _find_column(headers, ['transaction date', 'date', 'order date'])
    title_col = _find_column(headers, ['title', 'book title'])
    qty_col = _find_column(headers, ['quantity', 'units', 'qty'])
    earnings_col = _find_column(headers, ['earnings', 'revenue', 'amount', 'royalty'])
    currency_col = _find_column(headers, ['currency', 'currency code'])
    country_col = _find_column(headers, ['buyer country', 'country', 'territory'])
    txn_type_col = _find_column(headers, ['transaction type', 'type'])

    if date_col == -1:
        raise ParseError(f'Could not find date column in Google Play CSV. Headers: {headers}')
    if earnings_col == -1:
        raise ParseError(f'Could not find earnings column in Google Play CSV. Headers: {headers}')

    sales = []
    for row_num, row in enumerate(rows[1:], start=2):
        if not row or all(cell.strip() == '' for cell in row):
            continue

        try:
            date = row[date_col].strip() if date_col < len(row) else ''
            if not date:
                continue

            qty = _safe_int(row[qty_col]) if qty_col >= 0 and qty_col < len(row) else 0
            earnings = _safe_float(row[earnings_col]) if earnings_col < len(row) else 0.0
            currency = row[currency_col].strip() if currency_col >= 0 and currency_col < len(row) else 'USD'
            currency = currency or 'USD'
            country = row[country_col].strip() if country_col >= 0 and country_col < len(row) else ''

            txn_type = row[txn_type_col].strip().lower() if txn_type_col >= 0 and txn_type_col < len(row) else ''
            is_refund = 'refund' in txn_type or 'return' in txn_type or earnings < 0

            refund_amount = abs(earnings) if is_refund else 0.0
            royalty_amount = 0.0 if is_refund else earnings

            sale = {
                'book_id': book_id,
                'date': date,
                'units': abs(qty),
                'royalty_amount': royalty_amount,
                'currency': currency,
                'format': 'ebook',
                'marketplace': country,
                'platform': 'google',
                'refund_amount': refund_amount,
                'tax_withheld': 0.0,
                'royalty_rate': None,
                'row_hash': _row_hash(date, 'google', 'ebook', country),
            }
            sales.append(sale)

        except Exception as e:
            logger.warning(f'Skipping row {row_num}: {e}')
            continue

    logger.info(f'Parsed {len(sales)} records from Google Play CSV: {filepath}')
    return sales
