"""Tests for CLI commands."""

import os
import tempfile
import pytest
from click.testing import CliRunner
from price_optimizer.cli import main
from price_optimizer.db import Database


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def db_with_book():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = Database(path)
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
            bsr INTEGER, review_count INTEGER, avg_rating REAL,
            price REAL, kenp_pages_read INTEGER,
            timestamp TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            date TEXT NOT NULL, units INTEGER NOT NULL DEFAULT 0,
            royalty_amount REAL NOT NULL DEFAULT 0.0,
            currency TEXT DEFAULT 'USD', format TEXT DEFAULT '',
            marketplace TEXT DEFAULT 'US',
            UNIQUE(book_id, date, format, marketplace)
        );
    """)
    db.conn.execute(
        "INSERT INTO books (asin, title, author, format) VALUES (?, ?, ?, ?)",
        ('B0GMRN61MG', 'The Aethelred Cipher', 'Randy Pellegrini', 'ebook'),
    )
    db.conn.commit()
    db.close()
    yield path
    os.unlink(path)


class TestLogCommand:

    def test_log_price_change(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'log', '--asin', 'B0GMRN61MG', '--price', '4.99', '--reason', 'promo',
        ])
        assert result.exit_code == 0
        assert 'Logged price change' in result.output
        assert '$4.99' in result.output

    def test_log_with_old_price(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'log', '--asin', 'B0GMRN61MG', '--price', '0.99',
            '--old-price', '14.99', '--reason', 'launch promo',
        ])
        assert result.exit_code == 0
        assert '$14.99' in result.output
        assert '$0.99' in result.output

    def test_log_with_date(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'log', '--asin', 'B0GMRN61MG', '--price', '4.99',
            '--date', '2026-03-01',
        ])
        assert result.exit_code == 0

    def test_log_unknown_asin(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'log', '--asin', 'B0UNKNOWN', '--price', '4.99',
        ])
        assert result.exit_code == 0
        assert 'No book found' in result.output

    def test_log_paperback(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'log', '--asin', 'B0GMRN61MG', '--price', '14.99',
            '--format', 'paperback',
        ])
        assert result.exit_code == 0


class TestHistoryCommand:

    def test_history_empty(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'history', '--asin', 'B0GMRN61MG',
        ])
        assert result.exit_code == 0
        assert 'No price changes' in result.output

    def test_history_with_data(self, runner, db_with_book):
        # Log a price change first
        runner.invoke(main, [
            '--db', db_with_book,
            'log', '--asin', 'B0GMRN61MG', '--price', '4.99',
        ])
        result = runner.invoke(main, [
            '--db', db_with_book,
            'history', '--asin', 'B0GMRN61MG',
        ])
        assert result.exit_code == 0
        assert '4.99' in result.output

    def test_history_unknown_asin(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'history', '--asin', 'B0UNKNOWN',
        ])
        assert result.exit_code == 0
        assert 'No book found' in result.output


class TestAnalyzeCommand:

    def test_analyze_empty(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'analyze', '--asin', 'B0GMRN61MG',
        ])
        assert result.exit_code == 0
        assert 'No price data' in result.output

    def test_analyze_unknown_asin(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'analyze', '--asin', 'B0UNKNOWN',
        ])
        assert result.exit_code == 0
        assert 'No book found' in result.output


class TestRecommendCommand:

    def test_recommend_empty(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'recommend', '--asin', 'B0GMRN61MG',
        ])
        assert result.exit_code == 0
        assert 'No price history' in result.output

    def test_recommend_unknown_asin(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'recommend', '--asin', 'B0UNKNOWN',
        ])
        assert result.exit_code == 0
        assert 'No book found' in result.output


class TestRoyaltyCalcCommand:

    def test_ebook_royalty(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'royalty-calc', '--price', '4.99',
        ])
        assert result.exit_code == 0
        assert '70%' in result.output

    def test_paperback_royalty(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'royalty-calc', '--price', '14.99',
            '--format', 'paperback', '--print-cost', '4.50',
        ])
        assert result.exit_code == 0
        assert 'paperback' in result.output

    def test_royalty_json_output(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book, '--output', 'json',
            'royalty-calc', '--price', '4.99',
        ])
        assert result.exit_code == 0
        assert '"royalty_amount"' in result.output
        assert '"tier"' in result.output

    def test_royalty_with_pages(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book,
            'royalty-calc', '--price', '14.99',
            '--format', 'paperback', '--pages', '300',
        ])
        assert result.exit_code == 0


class TestJsonOutput:

    def test_history_json(self, runner, db_with_book):
        runner.invoke(main, [
            '--db', db_with_book,
            'log', '--asin', 'B0GMRN61MG', '--price', '4.99',
        ])
        result = runner.invoke(main, [
            '--db', db_with_book, '--output', 'json',
            'history', '--asin', 'B0GMRN61MG',
        ])
        assert result.exit_code == 0
        assert '"price_changes"' in result.output

    def test_analyze_json(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book, '--output', 'json',
            'analyze', '--asin', 'B0GMRN61MG',
        ])
        assert result.exit_code == 0

    def test_recommend_json(self, runner, db_with_book):
        result = runner.invoke(main, [
            '--db', db_with_book, '--output', 'json',
            'recommend', '--asin', 'B0GMRN61MG',
        ])
        assert result.exit_code == 0


class TestVersionAndConfig:

    def test_version(self, runner):
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert '0.1.0' in result.output

    def test_config(self, runner):
        result = runner.invoke(main, ['config'])
        assert result.exit_code == 0
        assert 'DB_PATH' in result.output
