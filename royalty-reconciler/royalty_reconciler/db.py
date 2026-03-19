import sqlite3
import logging
from typing import Optional, List
from .models import SaleRecord, Expense

logger = logging.getLogger(__name__)


class Database:
    """Lightweight database connection to the shared ~/.book-data/books.db.

    Schema and migrations are managed by book-data. This class reads/writes
    the sales and expenses tables, handling missing columns gracefully.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self):
        """Create tables if they don't exist (for standalone use without book-data)."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                author TEXT DEFAULT '',
                format TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
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

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER REFERENCES books(id) ON DELETE SET NULL,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                category TEXT NOT NULL,
                description TEXT DEFAULT '',
                tax_deductible INTEGER DEFAULT 1
            );

            CREATE INDEX IF NOT EXISTS idx_sales_book_id ON sales(book_id);
            CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date);
            CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
            CREATE INDEX IF NOT EXISTS idx_expenses_book ON expenses(book_id);
        """)
        # Add extended columns if missing (matches book-data migration 3)
        for col, typedef in [
            ('platform', "TEXT DEFAULT 'kdp'"),
            ('refund_amount', 'REAL DEFAULT 0.0'),
            ('tax_withheld', 'REAL DEFAULT 0.0'),
            ('royalty_rate', 'REAL'),
            ('payment_received', 'INTEGER DEFAULT 0'),
            ('payment_date', 'TEXT'),
        ]:
            try:
                self.conn.execute(f"ALTER TABLE sales ADD COLUMN {col} {typedef}")
            except sqlite3.OperationalError:
                pass  # column already exists
        self.conn.commit()

    def close(self):
        self.conn.close()

    # --- Books ---

    def get_book_by_asin(self, asin: str) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM books WHERE asin = ?", (asin,)).fetchone()
        if not row:
            return None
        return dict(row)

    def get_book_by_title(self, title: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM books WHERE title LIKE ?", (f'%{title}%',)
        ).fetchone()
        if not row:
            return None
        return dict(row)

    def list_books(self) -> List[dict]:
        rows = self.conn.execute("SELECT * FROM books ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def add_book(self, asin: str, title: str, author: str = '', fmt: str = '') -> int:
        cursor = self.conn.execute(
            "INSERT INTO books (asin, title, author, format) VALUES (?, ?, ?, ?)",
            (asin, title, author, fmt),
        )
        self.conn.commit()
        return cursor.lastrowid

    # --- Sales ---

    def _safe_get(self, row, col, default=None):
        try:
            return row[col] if col in row.keys() else default
        except Exception:
            return default

    def add_sales_bulk(self, sales: List[dict]) -> int:
        count = 0
        for s in sales:
            try:
                self.conn.execute(
                    """INSERT OR REPLACE INTO sales
                       (book_id, date, units, royalty_amount, currency, format, marketplace,
                        platform, refund_amount, tax_withheld, royalty_rate)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (s['book_id'], s['date'], s.get('units', 0),
                     s.get('royalty_amount', 0.0), s.get('currency', 'USD'),
                     s.get('format', ''), s.get('marketplace', 'US'),
                     s.get('platform', 'kdp'), s.get('refund_amount', 0.0),
                     s.get('tax_withheld', 0.0), s.get('royalty_rate')),
                )
                count += 1
            except sqlite3.IntegrityError as e:
                logger.warning(f"Skipping duplicate sale: {e}")
        self.conn.commit()
        return count

    def get_sales_by_month(self, year: int, month: int,
                           platform: str = None, book_id: int = None) -> List[dict]:
        query = """SELECT s.*, b.title, b.asin FROM sales s
                   JOIN books b ON s.book_id = b.id
                   WHERE strftime('%Y', s.date) = ? AND strftime('%m', s.date) = ?"""
        params: list = [str(year), f'{month:02d}']
        if platform:
            query += " AND s.platform = ?"
            params.append(platform)
        if book_id:
            query += " AND s.book_id = ?"
            params.append(book_id)
        query += " ORDER BY s.date ASC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_sales_by_year(self, year: int, platform: str = None,
                          book_id: int = None) -> List[dict]:
        query = """SELECT s.*, b.title, b.asin FROM sales s
                   JOIN books b ON s.book_id = b.id
                   WHERE strftime('%Y', s.date) = ?"""
        params: list = [str(year)]
        if platform:
            query += " AND s.platform = ?"
            params.append(platform)
        if book_id:
            query += " AND s.book_id = ?"
            params.append(book_id)
        query += " ORDER BY s.date ASC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_import_summary(self) -> List[dict]:
        """Get summary of imports grouped by platform."""
        rows = self.conn.execute("""
            SELECT platform,
                   COUNT(*) as record_count,
                   MIN(date) as earliest_date,
                   MAX(date) as latest_date,
                   SUM(units) as total_units,
                   ROUND(SUM(royalty_amount), 2) as total_royalties
            FROM sales
            GROUP BY platform
            ORDER BY platform
        """).fetchall()
        return [dict(r) for r in rows]

    def mark_payment_received(self, platform: str, year: int, month: int,
                              payment_date: str) -> int:
        cursor = self.conn.execute(
            """UPDATE sales SET payment_received = 1, payment_date = ?
               WHERE platform = ? AND strftime('%Y', date) = ?
               AND strftime('%m', date) = ?""",
            (payment_date, platform, str(year), f'{month:02d}'),
        )
        self.conn.commit()
        return cursor.rowcount

    # --- Expenses ---

    def add_expense(self, date: str, amount: float, category: str,
                    book_id: int = None, currency: str = 'USD',
                    description: str = '', tax_deductible: bool = True) -> int:
        cursor = self.conn.execute(
            """INSERT INTO expenses (book_id, date, amount, currency, category,
                                     description, tax_deductible)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (book_id, date, amount, currency, category, description,
             1 if tax_deductible else 0),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_expenses(self, year: int = None, month: int = None,
                     category: str = None) -> List[dict]:
        query = "SELECT * FROM expenses WHERE 1=1"
        params = []
        if year:
            query += " AND strftime('%Y', date) = ?"
            params.append(str(year))
        if month:
            query += " AND strftime('%m', date) = ?"
            params.append(f'{month:02d}')
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY date ASC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_expenses_by_category(self, year: int) -> dict:
        rows = self.conn.execute("""
            SELECT category, ROUND(SUM(amount), 2) as total
            FROM expenses
            WHERE strftime('%Y', date) = ?
            GROUP BY category
            ORDER BY total DESC
        """, (str(year),)).fetchall()
        return {r['category']: r['total'] for r in rows}
