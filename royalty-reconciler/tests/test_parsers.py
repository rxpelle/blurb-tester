"""Tests for platform parsers."""
import os
import tempfile
import pytest
from pathlib import Path

from royalty_reconciler.parsers import parse_file, detect_platform, ParseError
from royalty_reconciler.parsers.kdp import parse as parse_kdp
from royalty_reconciler.parsers.apple import parse as parse_apple
from royalty_reconciler.parsers.kobo import parse as parse_kobo
from royalty_reconciler.parsers.google import parse as parse_google
from royalty_reconciler.parsers.d2d import parse as parse_d2d
from royalty_reconciler.parsers.acx import parse as parse_acx

FIXTURES = Path(__file__).parent / 'fixtures'


# --- KDP Parser ---

class TestKDPParser:
    def test_parse_basic(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        assert len(records) == 4

    def test_parse_dates(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        assert records[0]['date'] == '2026-03-01'
        assert records[1]['date'] == '2026-03-02'

    def test_parse_units(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        assert records[0]['units'] == 1
        assert records[1]['units'] == 2

    def test_parse_royalty(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        assert records[0]['royalty_amount'] == 3.82
        assert records[1]['royalty_amount'] == 7.64

    def test_parse_currency(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        assert records[0]['currency'] == 'USD'
        assert records[2]['currency'] == 'GBP'

    def test_parse_platform_tag(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        assert all(r['platform'] == 'kdp' for r in records)

    def test_parse_refund(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        refund = records[3]
        assert refund['refund_amount'] == 3.82
        assert refund['royalty_amount'] == 0.0

    def test_parse_marketplace(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        assert records[0]['marketplace'] == 'Amazon.com'
        assert records[2]['marketplace'] == 'Amazon.co.uk'

    def test_parse_bom(self, kdp_bom_csv):
        records = parse_kdp(kdp_bom_csv, book_id=1)
        assert len(records) == 1
        assert records[0]['royalty_amount'] == 3.82

    def test_parse_empty_rows(self, kdp_empty_rows_csv):
        records = parse_kdp(kdp_empty_rows_csv, book_id=1)
        assert len(records) == 2

    def test_parse_royalty_rate(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        assert records[0]['royalty_rate'] == 0.7

    def test_parse_book_id(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=42)
        assert all(r['book_id'] == 42 for r in records)

    def test_parse_book_id_none(self, kdp_csv):
        records = parse_kdp(kdp_csv)
        assert all(r['book_id'] is None for r in records)

    def test_parse_row_hash(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        assert all(r['row_hash'] for r in records)
        # Different rows should have different hashes (when dates/markets differ)
        hashes = [r['row_hash'] for r in records]
        # records 0 and 3 have same date+market so same hash is expected
        assert hashes[0] != hashes[1]  # different dates

    def test_parse_empty_file(self, tmp_path):
        f = tmp_path / 'empty.csv'
        f.write_text('')
        with pytest.raises(ParseError):
            parse_kdp(str(f), book_id=1)

    def test_parse_bad_headers(self, tmp_path):
        f = tmp_path / 'bad.csv'
        f.write_text('Col1,Col2,Col3\n1,2,3\n')
        with pytest.raises(ParseError):
            parse_kdp(str(f), book_id=1)

    def test_parse_multi_currency(self, kdp_csv):
        records = parse_kdp(kdp_csv, book_id=1)
        currencies = set(r['currency'] for r in records)
        assert 'USD' in currencies
        assert 'GBP' in currencies


# --- Apple Parser ---

class TestAppleParser:
    def test_parse_basic(self, apple_csv):
        records = parse_apple(apple_csv, book_id=1)
        assert len(records) == 3

    def test_parse_date_normalization(self, apple_csv):
        records = parse_apple(apple_csv, book_id=1)
        # MM/DD/YYYY -> YYYY-MM-DD
        assert records[0]['date'] == '2026-03-01'

    def test_parse_units(self, apple_csv):
        records = parse_apple(apple_csv, book_id=1)
        assert records[0]['units'] == 2

    def test_parse_refund(self, apple_csv):
        records = parse_apple(apple_csv, book_id=1)
        refund = records[2]
        assert refund['refund_amount'] == 4.99
        assert refund['royalty_amount'] == 0.0
        assert refund['units'] == 1  # abs value

    def test_parse_platform_tag(self, apple_csv):
        records = parse_apple(apple_csv, book_id=1)
        assert all(r['platform'] == 'apple' for r in records)

    def test_parse_country(self, apple_csv):
        records = parse_apple(apple_csv, book_id=1)
        assert records[0]['marketplace'] == 'US'
        assert records[1]['marketplace'] == 'GB'

    def test_parse_currency(self, apple_csv):
        records = parse_apple(apple_csv, book_id=1)
        assert records[0]['currency'] == 'USD'
        assert records[1]['currency'] == 'GBP'


# --- Kobo Parser ---

class TestKoboParser:
    def test_parse_basic(self, kobo_csv):
        records = parse_kobo(kobo_csv, book_id=1)
        assert len(records) == 3

    def test_parse_royalty(self, kobo_csv):
        records = parse_kobo(kobo_csv, book_id=1)
        assert records[0]['royalty_amount'] == 2.80

    def test_parse_refund(self, kobo_csv):
        records = parse_kobo(kobo_csv, book_id=1)
        refund = records[2]
        assert refund['refund_amount'] == 2.80
        assert refund['royalty_amount'] == 0.0

    def test_parse_platform_tag(self, kobo_csv):
        records = parse_kobo(kobo_csv, book_id=1)
        assert all(r['platform'] == 'kobo' for r in records)

    def test_parse_multi_currency(self, kobo_csv):
        records = parse_kobo(kobo_csv, book_id=1)
        currencies = set(r['currency'] for r in records)
        assert 'USD' in currencies
        assert 'CAD' in currencies

    def test_parse_format(self, kobo_csv):
        records = parse_kobo(kobo_csv, book_id=1)
        assert all(r['format'] == 'ebook' for r in records)


# --- Google Play Parser ---

class TestGoogleParser:
    def test_parse_basic(self, google_csv):
        records = parse_google(google_csv, book_id=1)
        assert len(records) == 3

    def test_parse_earnings(self, google_csv):
        records = parse_google(google_csv, book_id=1)
        assert records[0]['royalty_amount'] == 3.50
        assert records[1]['royalty_amount'] == 7.00

    def test_parse_refund(self, google_csv):
        records = parse_google(google_csv, book_id=1)
        refund = records[2]
        assert refund['refund_amount'] == 3.50
        assert refund['royalty_amount'] == 0.0

    def test_parse_platform_tag(self, google_csv):
        records = parse_google(google_csv, book_id=1)
        assert all(r['platform'] == 'google' for r in records)

    def test_parse_quantity(self, google_csv):
        records = parse_google(google_csv, book_id=1)
        assert records[1]['units'] == 2

    def test_parse_country(self, google_csv):
        records = parse_google(google_csv, book_id=1)
        assert records[0]['marketplace'] == 'US'
        assert records[1]['marketplace'] == 'DE'


# --- D2D Parser ---

class TestD2DParser:
    def test_parse_basic(self, d2d_csv):
        records = parse_d2d(d2d_csv, book_id=1)
        assert len(records) == 3

    def test_parse_channel(self, d2d_csv):
        records = parse_d2d(d2d_csv, book_id=1)
        assert records[0]['marketplace'] == 'Apple Books'
        assert records[1]['marketplace'] == 'Barnes & Noble'

    def test_parse_royalty(self, d2d_csv):
        records = parse_d2d(d2d_csv, book_id=1)
        assert records[0]['royalty_amount'] == 2.10

    def test_parse_platform_tag(self, d2d_csv):
        records = parse_d2d(d2d_csv, book_id=1)
        assert all(r['platform'] == 'd2d' for r in records)

    def test_parse_format(self, d2d_csv):
        records = parse_d2d(d2d_csv, book_id=1)
        assert all(r['format'] == 'ebook' for r in records)


# --- ACX Parser ---

class TestACXParser:
    def test_parse_basic(self, acx_csv):
        records = parse_acx(acx_csv, book_id=1)
        assert len(records) == 3

    def test_parse_royalty(self, acx_csv):
        records = parse_acx(acx_csv, book_id=1)
        assert records[0]['royalty_amount'] == 12.50

    def test_parse_refund(self, acx_csv):
        records = parse_acx(acx_csv, book_id=1)
        refund = records[2]
        assert refund['refund_amount'] == 4.17
        assert refund['royalty_amount'] == 0.0

    def test_parse_marketplace(self, acx_csv):
        records = parse_acx(acx_csv, book_id=1)
        assert records[0]['marketplace'] == 'Audible.com'
        assert records[1]['marketplace'] == 'Audible.co.uk'

    def test_parse_format(self, acx_csv):
        records = parse_acx(acx_csv, book_id=1)
        assert all(r['format'] == 'audiobook' for r in records)

    def test_parse_platform_tag(self, acx_csv):
        records = parse_acx(acx_csv, book_id=1)
        assert all(r['platform'] == 'acx' for r in records)

    def test_parse_currency(self, acx_csv):
        records = parse_acx(acx_csv, book_id=1)
        assert records[0]['currency'] == 'USD'
        assert records[1]['currency'] == 'GBP'


# --- Platform Detection ---

class TestDetectPlatform:
    def test_detect_kdp(self, kdp_csv):
        assert detect_platform(kdp_csv) == 'kdp'

    def test_detect_apple(self, apple_csv):
        assert detect_platform(apple_csv) == 'apple'

    def test_detect_google(self, google_csv):
        assert detect_platform(google_csv) == 'google'

    def test_detect_d2d(self, d2d_csv):
        assert detect_platform(d2d_csv) == 'd2d'

    def test_detect_unknown(self, tmp_path):
        f = tmp_path / 'unknown.csv'
        f.write_text('Name,Age,City\nAlice,30,NYC\n')
        assert detect_platform(str(f)) == 'unknown'


# --- parse_file dispatcher ---

class TestParseFile:
    def test_dispatch_kdp(self, kdp_csv):
        records = parse_file(kdp_csv, 'kdp', book_id=1)
        assert len(records) == 4
        assert all(r['platform'] == 'kdp' for r in records)

    def test_dispatch_apple(self, apple_csv):
        records = parse_file(apple_csv, 'apple', book_id=1)
        assert len(records) == 3

    def test_dispatch_unknown_platform(self, kdp_csv):
        with pytest.raises(ParseError, match='Unknown platform'):
            parse_file(kdp_csv, 'nonexistent', book_id=1)

    def test_dispatch_case_insensitive(self, kdp_csv):
        records = parse_file(kdp_csv, 'KDP', book_id=1)
        assert len(records) == 4
