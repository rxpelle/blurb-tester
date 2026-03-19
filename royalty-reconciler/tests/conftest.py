import os
import tempfile
from pathlib import Path

import pytest

from royalty_reconciler.db import Database

FIXTURES_DIR = Path(__file__).parent / 'fixtures'


@pytest.fixture
def tmp_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = Database(path)
    yield db
    db.close()
    os.unlink(path)


@pytest.fixture
def sample_book(tmp_db):
    book_id = tmp_db.add_book(
        asin='B0GMRN61MG',
        title='The Aethelred Cipher',
        author='Randy Pellegrini',
        fmt='ebook',
    )
    return tmp_db, book_id


@pytest.fixture
def populated_db(sample_book):
    db, book_id = sample_book

    # Add sales from multiple platforms
    sales = [
        {'book_id': book_id, 'date': '2026-03-01', 'units': 1,
         'royalty_amount': 3.82, 'currency': 'USD', 'format': 'ebook',
         'marketplace': 'US', 'platform': 'kdp', 'refund_amount': 0.0,
         'tax_withheld': 0.0, 'royalty_rate': 0.7},
        {'book_id': book_id, 'date': '2026-03-02', 'units': 2,
         'royalty_amount': 7.64, 'currency': 'USD', 'format': 'ebook',
         'marketplace': 'US', 'platform': 'kdp', 'refund_amount': 0.0,
         'tax_withheld': 0.0, 'royalty_rate': 0.7},
        {'book_id': book_id, 'date': '2026-03-03', 'units': 1,
         'royalty_amount': 2.50, 'currency': 'GBP', 'format': 'ebook',
         'marketplace': 'UK', 'platform': 'kdp', 'refund_amount': 0.0,
         'tax_withheld': 0.0, 'royalty_rate': 0.7},
        {'book_id': book_id, 'date': '2026-03-01', 'units': 1,
         'royalty_amount': 2.80, 'currency': 'USD', 'format': 'ebook',
         'marketplace': 'US', 'platform': 'kobo', 'refund_amount': 0.0,
         'tax_withheld': 0.0, 'royalty_rate': None},
    ]
    db.add_sales_bulk(sales)

    # Add expenses
    db.add_expense(date='2026-03-01', amount=50.00, category='ads',
                   description='AMS campaign')
    db.add_expense(date='2026-03-05', amount=200.00, category='editing',
                   description='Copy edit')
    db.add_expense(date='2026-03-10', amount=25.00, category='tools',
                   description='Scrivener license')

    # Add second book
    book2_id = db.add_book(
        asin='B0TEST12345',
        title='The Genesis Protocol',
        author='Randy Pellegrini',
        fmt='ebook',
    )

    return db, book_id, book2_id


@pytest.fixture
def kdp_csv():
    return str(FIXTURES_DIR / 'kdp_sales.csv')


@pytest.fixture
def kdp_bom_csv():
    return str(FIXTURES_DIR / 'kdp_sales_bom.csv')


@pytest.fixture
def kdp_empty_rows_csv():
    return str(FIXTURES_DIR / 'kdp_empty_rows.csv')


@pytest.fixture
def apple_csv():
    return str(FIXTURES_DIR / 'apple_sales.csv')


@pytest.fixture
def kobo_csv():
    return str(FIXTURES_DIR / 'kobo_sales.csv')


@pytest.fixture
def google_csv():
    return str(FIXTURES_DIR / 'google_sales.csv')


@pytest.fixture
def d2d_csv():
    return str(FIXTURES_DIR / 'd2d_sales.csv')


@pytest.fixture
def acx_csv():
    return str(FIXTURES_DIR / 'acx_sales.csv')
