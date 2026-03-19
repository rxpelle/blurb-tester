import os
import json
import tempfile
import sqlite3
import pytest
from click.testing import CliRunner
from read_through_calc.cli import main


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


@pytest.fixture
def populated_db_path():
    """Create a temp DB with a 3-book series for CLI testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA_SQL)

    series = 'Test Series'
    conn.execute(
        "INSERT INTO books (asin, title, author, format, series_name, series_position, kenp_baseline) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ('B0CLI1', 'CLI Book 1', 'Author', 'ebook', series, 1, 300),
    )
    conn.execute(
        "INSERT INTO books (asin, title, author, format, series_name, series_position, kenp_baseline) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ('B0CLI2', 'CLI Book 2', 'Author', 'ebook', series, 2, 320),
    )
    conn.execute(
        "INSERT INTO books (asin, title, author, format, series_name, series_position, kenp_baseline) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ('B0CLI3', 'CLI Book 3', 'Author', 'ebook', series, 3, 350),
    )

    # Sales: 100, 50, 25
    for i in range(1, 101):
        d = min(i, 28)
        conn.execute(
            "INSERT OR REPLACE INTO sales (book_id, date, units, royalty_amount, currency, format, marketplace) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, f'2026-01-{d:02d}', 1, 3.49, 'USD', 'ebook', f'US-{i}'),
        )
    for i in range(1, 51):
        d = min(i, 28)
        conn.execute(
            "INSERT OR REPLACE INTO sales (book_id, date, units, royalty_amount, currency, format, marketplace) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (2, f'2026-01-{d:02d}', 1, 3.49, 'USD', 'ebook', f'US-{i}'),
        )
    for i in range(1, 26):
        conn.execute(
            "INSERT OR REPLACE INTO sales (book_id, date, units, royalty_amount, currency, format, marketplace) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (3, f'2026-01-{i:02d}', 1, 3.49, 'USD', 'ebook', f'US-{i}'),
        )

    # Snapshots
    conn.execute("INSERT INTO snapshots (book_id, price) VALUES (1, 4.99)")
    conn.execute("INSERT INTO snapshots (book_id, price) VALUES (2, 4.99)")
    conn.execute("INSERT INTO snapshots (book_id, price) VALUES (3, 4.99)")

    conn.commit()
    conn.close()
    yield path
    os.unlink(path)


@pytest.fixture
def empty_db_path():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    yield path
    os.unlink(path)


@pytest.fixture
def runner():
    return CliRunner()


class TestReportCommand:
    def test_report_table(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'report'])
        assert result.exit_code == 0
        assert 'Read-Through' in result.output

    def test_report_series_filter(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'report', '--series', 'Test Series'])
        assert result.exit_code == 0
        assert 'Read-Through' in result.output

    def test_report_json(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, '-o', 'json', 'report'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'series' in data
        assert 'rates' in data

    def test_report_empty_db(self, runner, empty_db_path):
        result = runner.invoke(main, ['--db', empty_db_path, 'report'])
        assert result.exit_code == 0
        assert 'No series found' in result.output

    def test_report_nonexistent_series(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'report', '--series', 'Fake Series'])
        assert result.exit_code == 0

    def test_report_with_window(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'report', '--window', '30'])
        assert result.exit_code == 0


class TestLTVCommand:
    def test_ltv_table(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'ltv'])
        assert result.exit_code == 0
        assert 'Lifetime Reader Value' in result.output

    def test_ltv_series_filter(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'ltv', '--series', 'Test Series'])
        assert result.exit_code == 0
        assert 'Lifetime Reader Value' in result.output

    def test_ltv_json(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, '-o', 'json', 'ltv'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'total_ltv' in data
        assert 'books' in data

    def test_ltv_empty_db(self, runner, empty_db_path):
        result = runner.invoke(main, ['--db', empty_db_path, 'ltv'])
        assert result.exit_code == 0
        assert 'No series found' in result.output

    def test_ltv_custom_kenp_rate(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'ltv', '--kenp-rate', '0.005'])
        assert result.exit_code == 0


class TestPricingCommand:
    def test_pricing_basic(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'pricing',
                                      '--book1-price', '0.99', '--book2-price', '4.99',
                                      '--book3-price', '4.99'])
        assert result.exit_code == 0
        assert 'Pricing Scenario' in result.output

    def test_pricing_series_filter(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'pricing',
                                      '--series', 'Test Series', '--book1-price', '2.99'])
        assert result.exit_code == 0

    def test_pricing_json(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, '-o', 'json', 'pricing',
                                      '--book1-price', '0.99', '--book2-price', '4.99'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'total_ltv' in data
        assert 'revenue_per_100_readers' in data

    def test_pricing_no_prices(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'pricing'])
        assert result.exit_code == 0
        assert 'Provide at least' in result.output

    def test_pricing_empty_db(self, runner, empty_db_path):
        result = runner.invoke(main, ['--db', empty_db_path, 'pricing', '--book1-price', '2.99'])
        assert result.exit_code == 0
        assert 'No series found' in result.output

    def test_pricing_partial_prices(self, runner, populated_db_path):
        result = runner.invoke(main, ['--db', populated_db_path, 'pricing',
                                      '--book1-price', '0.99'])
        assert result.exit_code == 0


class TestConfigCommand:
    def test_config(self, runner):
        result = runner.invoke(main, ['config'])
        assert result.exit_code == 0
        assert 'DB_PATH' in result.output
        assert 'KU_PAGE_RATE' in result.output


class TestVersionFlag:
    def test_version(self, runner):
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert '0.1.0' in result.output
