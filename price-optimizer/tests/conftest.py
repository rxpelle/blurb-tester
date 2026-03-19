import os
import tempfile
import json
import pytest
from price_optimizer.db import Database


@pytest.fixture
def tmp_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = Database(path)
    # Create the books table (since this tool connects to shared DB
    # but in tests we need a fresh DB with schema)
    db.conn.executescript("""
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
            UNIQUE(book_id, date, format, marketplace)
        );
    """)
    db.conn.commit()
    yield db
    db.close()
    os.unlink(path)


@pytest.fixture
def sample_book(tmp_db):
    cursor = tmp_db.conn.execute(
        """INSERT INTO books (asin, title, author, format, kenp_baseline)
           VALUES (?, ?, ?, ?, ?)""",
        ('B0GMRN61MG', 'The Aethelred Cipher', 'Randy Pellegrini', 'ebook', 350),
    )
    tmp_db.conn.commit()
    book_id = cursor.lastrowid
    return tmp_db, book_id


@pytest.fixture
def price_history_db(sample_book):
    """Book with price changes at $14.99 for 30 days, then $4.99 for 30 days.

    At $14.99: 2 units over 30 days (low volume)
    At $4.99: 10 units over 30 days (higher volume)
    BSR snapshots at each price point.
    """
    db, book_id = sample_book

    # Price change 1: $14.99 starting 2026-01-15
    db.add_price_change(
        book_id=book_id, new_price=14.99, old_price=None,
        format='ebook', marketplace='US', reason='launch price',
        changed_at='2026-01-15',
    )

    # Price change 2: $4.99 starting 2026-02-14
    db.add_price_change(
        book_id=book_id, new_price=4.99, old_price=14.99,
        format='ebook', marketplace='US', reason='promo',
        changed_at='2026-02-14',
    )

    # Sales at $14.99 (2 units over 30 days)
    db.conn.execute(
        "INSERT INTO sales (book_id, date, units, royalty_amount, currency, format, marketplace) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (book_id, '2026-01-20', 1, 10.49, 'USD', 'ebook', 'US'),
    )
    db.conn.execute(
        "INSERT INTO sales (book_id, date, units, royalty_amount, currency, format, marketplace) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (book_id, '2026-02-05', 1, 10.49, 'USD', 'ebook', 'US'),
    )

    # Sales at $4.99 (10 units over 30 days)
    for i in range(10):
        day = 14 + i * 3
        date = f'2026-02-{day:02d}' if day <= 28 else f'2026-03-{day - 28:02d}'
        db.conn.execute(
            "INSERT OR REPLACE INTO sales (book_id, date, units, royalty_amount, currency, format, marketplace) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (book_id, date, 1, 3.42, 'USD', 'ebook', 'US'),
        )

    # BSR snapshots at $14.99 — high BSR (bad rank)
    for ts in ['2026-01-20 10:00:00', '2026-01-27 10:00:00', '2026-02-05 10:00:00']:
        db.conn.execute(
            "INSERT INTO snapshots (book_id, bsr, review_count, avg_rating, price, kenp_pages_read, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (book_id, 500000, 50, 4.8, 14.99, 400, ts),
        )

    # BSR snapshots at $4.99 — lower BSR (better rank)
    for ts in ['2026-02-20 10:00:00', '2026-02-27 10:00:00', '2026-03-05 10:00:00']:
        db.conn.execute(
            "INSERT INTO snapshots (book_id, bsr, review_count, avg_rating, price, kenp_pages_read, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (book_id, 100000, 52, 4.8, 4.99, 500, ts),
        )

    db.conn.commit()
    return db, book_id


@pytest.fixture
def experiments_file():
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def experiments_file_with_data(experiments_file):
    data = {
        'experiments': [
            {
                'asin': 'B0GMRN61MG',
                'prices': [2.99, 4.99],
                'duration_days': 14,
                'started_at': '2026-03-01',
                'current_price_index': 0,
                'status': 'running',
            },
            {
                'asin': 'B0TEST12345',
                'prices': [0.99, 2.99, 4.99],
                'duration_days': 7,
                'started_at': '2026-01-01',
                'current_price_index': 2,
                'status': 'completed',
            },
        ]
    }
    with open(experiments_file, 'w') as f:
        json.dump(data, f)
    return experiments_file
