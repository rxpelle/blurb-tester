"""Apple Books Connect CSV parser.

Expected columns:
  Vendor Identifier, Title, Product Type Identifier, Units,
  Royalty Currency, Royalty Price, Begin Date, End Date, Country Code
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
    """Parse an Apple Books Connect royalty CSV."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    reader = csv.reader(StringIO(content), delimiter='\t')
    rows = list(reader)

    # Apple uses tab-delimited; fall back to comma if tabs don't produce enough columns
    if rows and len(rows[0]) <= 1:
        reader = csv.reader(StringIO(content))
        rows = list(reader)

    if not rows:
        raise ParseError('Empty CSV file')

    headers = rows[0]

    vendor_col = _find_column(headers, ['vendor identifier', 'apple identifier', 'apple id'])
    title_col = _find_column(headers, ['title'])
    type_col = _find_column(headers, ['product type identifier', 'product type'])
    units_col = _find_column(headers, ['units', 'quantity'])
    currency_col = _find_column(headers, ['royalty currency', 'currency code', 'currency'])
    royalty_col = _find_column(headers, ['royalty price', 'royalty', 'developer proceeds'])
    begin_date_col = _find_column(headers, ['begin date', 'start date'])
    end_date_col = _find_column(headers, ['end date'])
    country_col = _find_column(headers, ['country code', 'country', 'territory'])

    if begin_date_col == -1:
        raise ParseError(f'Could not find date column in Apple CSV. Headers: {headers}')
    if royalty_col == -1:
        raise ParseError(f'Could not find royalty column in Apple CSV. Headers: {headers}')

    sales = []
    for row_num, row in enumerate(rows[1:], start=2):
        if not row or all(cell.strip() == '' for cell in row):
            continue

        try:
            date = row[begin_date_col].strip() if begin_date_col < len(row) else ''
            if not date:
                continue

            # Normalize Apple date formats (MM/DD/YYYY -> YYYY-MM-DD)
            if '/' in date:
                parts = date.split('/')
                if len(parts) == 3:
                    date = f'{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}'

            units = _safe_int(row[units_col]) if units_col >= 0 and units_col < len(row) else 0
            royalty = _safe_float(row[royalty_col]) if royalty_col < len(row) else 0.0
            currency = row[currency_col].strip() if currency_col >= 0 and currency_col < len(row) else 'USD'
            currency = currency or 'USD'
            country = row[country_col].strip() if country_col >= 0 and country_col < len(row) else 'US'
            fmt = row[type_col].strip() if type_col >= 0 and type_col < len(row) else 'ebook'

            # Negative units = refund
            is_refund = units < 0 or royalty < 0
            refund_amount = abs(royalty) if is_refund else 0.0
            royalty_amount = 0.0 if is_refund else royalty

            sale = {
                'book_id': book_id,
                'date': date,
                'units': abs(units),
                'royalty_amount': royalty_amount,
                'currency': currency,
                'format': fmt,
                'marketplace': country,
                'platform': 'apple',
                'refund_amount': refund_amount,
                'tax_withheld': 0.0,
                'royalty_rate': None,
                'row_hash': _row_hash(date, 'apple', fmt, country),
            }
            sales.append(sale)

        except Exception as e:
            logger.warning(f'Skipping row {row_num}: {e}')
            continue

    logger.info(f'Parsed {len(sales)} records from Apple CSV: {filepath}')
    return sales
