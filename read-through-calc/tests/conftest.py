import os
import tempfile
import sqlite3
import pytest
from read_through_calc.db import ReadOnlyDB


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    author TEXT DEFAULT '',
    format TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    word_count INTEGER,
    kenp_baseline INTEGER,
    series_name TEXT DEFAULT '',
    series_position INTEGER
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    bsr INTEGER,
    review_count INTEGER,
    avg_rating REAL,
    price REAL,
    kenp_pages_read INTEGER,
    timestamp TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    units INTEGER NOT NULL DEFAULT 0,
    royalty_amount REAL NOT NULL DEFAULT 0.0,
    currency TEXT DEFAULT 'USD',
    format TEXT DEFAULT '',
    marketplace TEXT DEFAULT 'US',
    platform TEXT DEFAULT 'kdp',
    refund_amount REAL DEFAULT 0.0,
    tax_withheld REAL DEFAULT 0.0,
    royalty_rate REAL,
    UNIQUE(book_id, date, format, marketplace)
);

CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL DEFAULT 0);
INSERT INTO schema_version (version) VALUES (3);
"""


def _create_test_db(path):
    """Create a test database with the shared schema."""
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def _add_book(conn, asin, title, series_name='', series_position=None,
              kenp_baseline=None, author='Randy Pellegrini'):
    cursor = conn.execute(
        """INSERT INTO books (asin, title, author, format, series_name, series_position, kenp_baseline)
           VALUES (?, ?, ?, 'ebook', ?, ?, ?)""",
        (asin, title, author, series_name, series_position, kenp_baseline),
    )
    conn.commit()
    return cursor.lastrowid


def _add_sale(conn, book_id, date, units, royalty_amount, marketplace='US'):
    conn.execute(
        """INSERT OR REPLACE INTO sales (book_id, date, units, royalty_amount, currency, format, marketplace)
           VALUES (?, ?, ?, ?, 'USD', 'ebook', ?)""",
        (book_id, date, units, royalty_amount, marketplace),
    )
    conn.commit()


def _add_snapshot(conn, book_id, price, bsr=None, review_count=None, avg_rating=None):
    conn.execute(
        """INSERT INTO snapshots (book_id, bsr, review_count, avg_rating, price)
           VALUES (?, ?, ?, ?, ?)""",
        (book_id, bsr, review_count, avg_rating, price),
    )
    conn.commit()


@pytest.fixture
def empty_db():
    """Empty database with schema but no data."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = _create_test_db(path)
    conn.close()
    db = ReadOnlyDB(path)
    yield db
    db.close()
    os.unlink(path)


@pytest.fixture
def series_3book_db():
    """
    3-book series with realistic sales data:
    - Book 1: 100 units total, $3.49 avg royalty, 350 KENP baseline
    - Book 2: 45 units total, $3.49 avg royalty, 380 KENP baseline
    - Book 3: 20 units total, $3.49 avg royalty, 400 KENP baseline

    Sales spread across months for cohort testing:
    - Jan 2026: Book 1 = 40 units, Book 2 = 18 units, Book 3 = 8 units
    - Feb 2026: Book 1 = 35 units, Book 2 = 16 units, Book 3 = 7 units
    - Mar 2026: Book 1 = 25 units, Book 2 = 11 units, Book 3 = 5 units

    Expected overall RT: 45/100 = 45%, 20/45 = 44.4%
    """
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = _create_test_db(path)

    series = 'The Architecture of Survival'

    b1_id = _add_book(conn, 'B0BOOK1ASIN', 'The Aethelred Cipher',
                       series, 1, kenp_baseline=350)
    b2_id = _add_book(conn, 'B0BOOK2ASIN', 'The Genesis Protocol',
                       series, 2, kenp_baseline=380)
    b3_id = _add_book(conn, 'B0BOOK3ASIN', 'The First Key',
                       series, 3, kenp_baseline=400)

    # January 2026 sales
    for day in range(1, 41):
        d = day if day <= 31 else 31
        _add_sale(conn, b1_id, f'2026-01-{d:02d}', 1, 3.49, f'US-jan-{day}')
    for day in range(1, 19):
        _add_sale(conn, b2_id, f'2026-01-{day:02d}', 1, 3.49, f'US-jan-{day}')
    for day in range(1, 9):
        _add_sale(conn, b3_id, f'2026-01-{day:02d}', 1, 3.49, f'US-jan-{day}')

    # February 2026 sales
    for day in range(1, 36):
        d = min(day, 28)
        _add_sale(conn, b1_id, f'2026-02-{d:02d}', 1, 3.49, f'US-feb-{day}')
    for day in range(1, 17):
        _add_sale(conn, b2_id, f'2026-02-{day:02d}', 1, 3.49, f'US-feb-{day}')
    for day in range(1, 8):
        _add_sale(conn, b3_id, f'2026-02-{day:02d}', 1, 3.49, f'US-feb-{day}')

    # March 2026 sales
    for day in range(1, 26):
        _add_sale(conn, b1_id, f'2026-03-{day:02d}', 1, 3.49, f'US-mar-{day}')
    for day in range(1, 12):
        _add_sale(conn, b2_id, f'2026-03-{day:02d}', 1, 3.49, f'US-mar-{day}')
    for day in range(1, 6):
        _add_sale(conn, b3_id, f'2026-03-{day:02d}', 1, 3.49, f'US-mar-{day}')

    # Snapshots with prices
    _add_snapshot(conn, b1_id, price=4.99, bsr=50000, review_count=52, avg_rating=4.8)
    _add_snapshot(conn, b2_id, price=4.99, bsr=80000, review_count=10, avg_rating=4.5)
    _add_snapshot(conn, b3_id, price=4.99, bsr=120000, review_count=3, avg_rating=4.7)

    conn.close()
    db = ReadOnlyDB(path)
    yield db, b1_id, b2_id, b3_id
    db.close()
    os.unlink(path)


@pytest.fixture
def series_2book_db():
    """2-book series: Book 1 = 50 units, Book 2 = 25 units (50% RT)."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = _create_test_db(path)

    series = 'Two Book Series'
    b1_id = _add_book(conn, 'B02BOOK1', 'Book One', series, 1, kenp_baseline=300)
    b2_id = _add_book(conn, 'B02BOOK2', 'Book Two', series, 2, kenp_baseline=320)

    for day in range(1, 51):
        d = min(day, 28)
        _add_sale(conn, b1_id, f'2026-01-{d:02d}', 1, 3.49, f'US-{day}')
    for day in range(1, 26):
        _add_sale(conn, b2_id, f'2026-01-{day:02d}', 1, 3.49, f'US-{day}')

    _add_snapshot(conn, b1_id, price=2.99)
    _add_snapshot(conn, b2_id, price=4.99)

    conn.close()
    db = ReadOnlyDB(path)
    yield db, b1_id, b2_id
    db.close()
    os.unlink(path)


@pytest.fixture
def series_5book_db():
    """5-book series with decreasing read-through."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = _create_test_db(path)

    series = 'Epic Five'
    units = [200, 120, 80, 50, 30]
    book_ids = []

    for i in range(5):
        bid = _add_book(conn, f'B05BOOK{i+1}', f'Epic Book {i+1}',
                         series, i + 1, kenp_baseline=300 + i * 20)
        book_ids.append(bid)
        for day in range(1, units[i] + 1):
            d = min(day, 28)
            _add_sale(conn, bid, f'2026-01-{d:02d}', 1, 3.49, f'US-{day}')
        _add_snapshot(conn, bid, price=4.99)

    conn.close()
    db = ReadOnlyDB(path)
    yield db, book_ids
    db.close()
    os.unlink(path)


@pytest.fixture
def single_book_db():
    """Single book, no series (series_name set but only 1 book)."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = _create_test_db(path)

    bid = _add_book(conn, 'B0SINGLE', 'Solo Book', 'Solo Series', 1, kenp_baseline=400)
    for day in range(1, 21):
        _add_sale(conn, bid, f'2026-01-{day:02d}', 1, 3.49, f'US-{day}')
    _add_snapshot(conn, bid, price=4.99)

    conn.close()
    db = ReadOnlyDB(path)
    yield db, bid
    db.close()
    os.unlink(path)


@pytest.fixture
def no_series_db():
    """Books with no series_name or series_position set."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = _create_test_db(path)

    _add_book(conn, 'B0NOSERIES1', 'Orphan Book 1')
    _add_book(conn, 'B0NOSERIES2', 'Orphan Book 2')

    conn.close()
    db = ReadOnlyDB(path)
    yield db
    db.close()
    os.unlink(path)


@pytest.fixture
def zero_sales_db():
    """Series with books but zero sales."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = _create_test_db(path)

    series = 'Zero Sales Series'
    _add_book(conn, 'B0ZERO1', 'Zero Book 1', series, 1, kenp_baseline=300)
    _add_book(conn, 'B0ZERO2', 'Zero Book 2', series, 2, kenp_baseline=320)

    conn.close()
    db = ReadOnlyDB(path)
    yield db
    db.close()
    os.unlink(path)


@pytest.fixture
def no_kenp_db():
    """Series where books have no kenp_baseline set."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = _create_test_db(path)

    series = 'No KENP Series'
    b1 = _add_book(conn, 'B0NOKENP1', 'No KENP Book 1', series, 1)
    b2 = _add_book(conn, 'B0NOKENP2', 'No KENP Book 2', series, 2)

    for day in range(1, 11):
        _add_sale(conn, b1, f'2026-01-{day:02d}', 1, 3.49, f'US-{day}')
    for day in range(1, 6):
        _add_sale(conn, b2, f'2026-01-{day:02d}', 1, 3.49, f'US-{day}')

    _add_snapshot(conn, b1, price=4.99)
    _add_snapshot(conn, b2, price=4.99)

    conn.close()
    db = ReadOnlyDB(path)
    yield db
    db.close()
    os.unlink(path)


@pytest.fixture
def high_rt_db():
    """Series where Book 2 has more sales than Book 1 (RT capped at 1.0)."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = _create_test_db(path)

    series = 'High RT Series'
    b1 = _add_book(conn, 'B0HIGH1', 'High RT Book 1', series, 1, kenp_baseline=300)
    b2 = _add_book(conn, 'B0HIGH2', 'High RT Book 2', series, 2, kenp_baseline=320)

    for day in range(1, 11):
        _add_sale(conn, b1, f'2026-01-{day:02d}', 1, 3.49, f'US-{day}')
    for day in range(1, 16):
        _add_sale(conn, b2, f'2026-01-{day:02d}', 1, 3.49, f'US-{day}')

    conn.close()
    db = ReadOnlyDB(path)
    yield db
    db.close()
    os.unlink(path)
