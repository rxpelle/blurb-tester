"""KDP (Kindle Direct Publishing) CSV parser.

Expected columns:
  Date, Title, Author, ASIN, Marketplace, Royalty Type, Transaction Type,
  Units Sold, Royalty, Currency
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
        candidate_lower = candidate.lower()
        for i, h in enumerate(headers_lower):
            if h == candidate_lower:
                return i
    for candidate in candidates:
        candidate_lower = candidate.lower()
        for i, h in enumerate(headers_lower):
            if candidate_lower in h:
                return i
    return -1


def _safe_int(val: str) -> int:
    try:
        return int(val.strip().replace(',', ''))
    except (ValueError, AttributeError):
        return 0


def _safe_float(val: str) -> float:
    try:
        return float(val.strip().replace(',', '').replace('$', ''))
    except (ValueError, AttributeError):
        return 0.0


def _row_hash(date: str, platform: str, fmt: str, marketplace: str) -> str:
    key = f"{date}|{platform}|{fmt}|{marketplace}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


def parse(filepath: str, book_id: int = None) -> List[dict]:
    """Parse a KDP royalty CSV file."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    reader = csv.reader(StringIO(content))
    rows = list(reader)

    if not rows:
        raise ParseError('Empty CSV file')

    headers = rows[0]
    headers_lower = [h.lower().strip() for h in headers]

    # Validate this looks like a KDP file
    has_royalty = any('royalty' in h or 'units' in h for h in headers_lower)
    if not has_royalty:
        raise ParseError(f'Does not appear to be a KDP CSV. Headers: {headers}')

    date_col = _find_column(headers, ['date', 'order date', 'transaction date'])
    title_col = _find_column(headers, ['title', 'book title'])
    asin_col = _find_column(headers, ['asin'])
    units_col = _find_column(headers, ['units sold', 'units ordered', 'units'])
    royalty_col = _find_column(headers, ['royalty', 'royalties', 'estimated royalty'])
    currency_col = _find_column(headers, ['currency', 'royalty currency'])
    format_col = _find_column(headers, ['product type', 'format', 'type'])
    marketplace_col = _find_column(headers, ['marketplace', 'territory'])
    txn_type_col = _find_column(headers, ['transaction type'])
    royalty_type_col = _find_column(headers, ['royalty type', 'royalty rate'])

    if date_col == -1:
        raise ParseError(f'Could not find date column in headers: {headers}')

    sales = []
    for row_num, row in enumerate(rows[1:], start=2):
        if not row or all(cell.strip() == '' for cell in row):
            continue

        try:
            date = row[date_col].strip() if date_col < len(row) else ''
            if not date:
                continue

            units = _safe_int(row[units_col]) if units_col >= 0 and units_col < len(row) else 0
            royalty = _safe_float(row[royalty_col]) if royalty_col >= 0 and royalty_col < len(row) else 0.0
            currency = row[currency_col].strip() if currency_col >= 0 and currency_col < len(row) else 'USD'
            currency = currency or 'USD'
            fmt = row[format_col].strip() if format_col >= 0 and format_col < len(row) else ''
            marketplace = row[marketplace_col].strip() if marketplace_col >= 0 and marketplace_col < len(row) else 'US'
            marketplace = marketplace or 'US'

            # Detect refunds
            txn_type = row[txn_type_col].strip().lower() if txn_type_col >= 0 and txn_type_col < len(row) else ''
            is_refund = 'refund' in txn_type or 'return' in txn_type

            refund_amount = abs(royalty) if is_refund else 0.0
            royalty_amount = 0.0 if is_refund else royalty

            # Parse royalty rate
            royalty_rate = None
            if royalty_type_col >= 0 and royalty_type_col < len(row):
                rate_str = row[royalty_type_col].strip().replace('%', '')
                try:
                    royalty_rate = float(rate_str) / 100.0
                except ValueError:
                    pass

            sale = {
                'book_id': book_id,
                'date': date,
                'units': abs(units) if is_refund else units,
                'royalty_amount': royalty_amount,
                'currency': currency,
                'format': fmt,
                'marketplace': marketplace,
                'platform': 'kdp',
                'refund_amount': refund_amount,
                'tax_withheld': 0.0,
                'royalty_rate': royalty_rate,
                'row_hash': _row_hash(date, 'kdp', fmt, marketplace),
            }
            sales.append(sale)

        except Exception as e:
            logger.warning(f'Skipping row {row_num}: {e}')
            continue

    logger.info(f'Parsed {len(sales)} records from KDP CSV: {filepath}')
    return sales
