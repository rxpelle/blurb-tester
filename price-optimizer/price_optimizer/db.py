import sqlite3
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Book:
    id: Optional[int] = None
    asin: str = ''
    title: str = ''
    author: str = ''
    format: str = ''
    created_at: str = ''
    word_count: Optional[int] = None
    kenp_baseline: Optional[int] = None
    series_name: str = ''
    series_position: Optional[int] = None


@dataclass
class Snapshot:
    id: Optional[int] = None
    book_id: Optional[int] = None
    bsr: Optional[int] = None
    review_count: Optional[int] = None
    avg_rating: Optional[float] = None
    price: Optional[float] = None
    kenp_pages_read: Optional[int] = None
    timestamp: str = ''


@dataclass
class Sale:
    id: Optional[int] = None
    book_id: Optional[int] = None
    date: str = ''
    units: int = 0
    royalty_amount: float = 0.0
    currency: str = 'USD'
    format: str = ''
    marketplace: str = 'US'


@dataclass
class PriceChange:
    id: Optional[int] = None
    book_id: Optional[int] = None
    old_price: Optional[float] = None
    new_price: float = 0.0
    format: str = 'ebook'
    marketplace: str = 'US'
    changed_at: str = ''
    reason: str = ''


class Database:
    """Connects to the shared ~/.book-data/books.db database.

    This tool reads from books, snapshots, sales and writes to price_changes.
    Schema creation/migration is handled by the book-data tool.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._ensure_price_changes_table()

    def _ensure_price_changes_table(self):
        """Create price_changes table if it doesn't exist (in case book-data hasn't run yet)."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS price_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                old_price REAL,
                new_price REAL NOT NULL,
                format TEXT DEFAULT 'ebook',
                marketplace TEXT DEFAULT 'US',
                changed_at TEXT NOT NULL DEFAULT (datetime('now')),
                reason TEXT DEFAULT ''
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_price_changes_book ON price_changes(book_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_price_changes_date ON price_changes(changed_at)")
        self.conn.commit()

    def close(self):
        self.conn.close()

    # --- Books (read-only) ---

    def get_book_by_asin(self, asin: str) -> Optional[Book]:
        row = self.conn.execute("SELECT * FROM books WHERE asin = ?", (asin,)).fetchone()
        if not row:
            return None
        return self._row_to_book(row)

    def list_books(self) -> List[Book]:
        rows = self.conn.execute("SELECT * FROM books ORDER BY created_at DESC").fetchall()
        return [self._row_to_book(r) for r in rows]

    # --- Snapshots (read-only) ---

    def get_snapshots(self, book_id: int, days: int = 365) -> List[Snapshot]:
        rows = self.conn.execute(
            """SELECT * FROM snapshots WHERE book_id = ?
               AND timestamp >= datetime('now', ?)
               ORDER BY timestamp ASC""",
            (book_id, f'-{days} days'),
        ).fetchall()
        return [self._row_to_snapshot(r) for r in rows]

    def get_snapshots_by_date_range(self, book_id: int, start: str, end: str) -> List[Snapshot]:
        rows = self.conn.execute(
            """SELECT * FROM snapshots WHERE book_id = ?
               AND timestamp >= ? AND timestamp <= ?
               ORDER BY timestamp ASC""",
            (book_id, start, end),
        ).fetchall()
        return [self._row_to_snapshot(r) for r in rows]

    # --- Sales (read-only) ---

    def get_sales_by_date_range(self, book_id: int, start: str, end: str) -> List[Sale]:
        rows = self.conn.execute(
            """SELECT * FROM sales WHERE book_id = ?
               AND date >= ? AND date <= ?
               ORDER BY date ASC""",
            (book_id, start, end),
        ).fetchall()
        return [self._row_to_sale(r) for r in rows]

    def get_sales(self, book_id: int, days: int = 365) -> List[Sale]:
        rows = self.conn.execute(
            """SELECT * FROM sales WHERE book_id = ?
               AND date >= date('now', ?)
               ORDER BY date ASC""",
            (book_id, f'-{days} days'),
        ).fetchall()
        return [self._row_to_sale(r) for r in rows]

    # --- Price Changes (read + write) ---

    def add_price_change(self, book_id: int, new_price: float, old_price: float = None,
                         format: str = 'ebook', marketplace: str = 'US',
                         reason: str = '', changed_at: str = None) -> int:
        if changed_at:
            cursor = self.conn.execute(
                """INSERT INTO price_changes (book_id, old_price, new_price, format, marketplace, reason, changed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (book_id, old_price, new_price, format, marketplace, reason, changed_at),
            )
        else:
            cursor = self.conn.execute(
                """INSERT INTO price_changes (book_id, old_price, new_price, format, marketplace, reason)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (book_id, old_price, new_price, format, marketplace, reason),
            )
        self.conn.commit()
        return cursor.lastrowid

    def get_price_changes(self, book_id: int) -> List[PriceChange]:
        rows = self.conn.execute(
            "SELECT * FROM price_changes WHERE book_id = ? ORDER BY changed_at ASC",
            (book_id,),
        ).fetchall()
        return [self._row_to_price_change(r) for r in rows]

    # --- Row converters ---

    @staticmethod
    def _row_to_book(row) -> Book:
        keys = row.keys()
        return Book(
            id=row['id'], asin=row['asin'], title=row['title'],
            author=row['author'], format=row['format'],
            created_at=row['created_at'],
            word_count=row['word_count'] if 'word_count' in keys else None,
            kenp_baseline=row['kenp_baseline'] if 'kenp_baseline' in keys else None,
            series_name=row['series_name'] if 'series_name' in keys else '',
            series_position=row['series_position'] if 'series_position' in keys else None,
        )

    @staticmethod
    def _row_to_snapshot(row) -> Snapshot:
        return Snapshot(
            id=row['id'], book_id=row['book_id'], bsr=row['bsr'],
            review_count=row['review_count'], avg_rating=row['avg_rating'],
            price=row['price'], kenp_pages_read=row['kenp_pages_read'],
            timestamp=row['timestamp'],
        )

    @staticmethod
    def _row_to_sale(row) -> Sale:
        return Sale(
            id=row['id'], book_id=row['book_id'], date=row['date'],
            units=row['units'], royalty_amount=row['royalty_amount'],
            currency=row['currency'], format=row['format'],
            marketplace=row['marketplace'],
        )

    @staticmethod
    def _row_to_price_change(row) -> PriceChange:
        return PriceChange(
            id=row['id'], book_id=row['book_id'],
            old_price=row['old_price'], new_price=row['new_price'],
            format=row['format'], marketplace=row['marketplace'],
            changed_at=row['changed_at'], reason=row['reason'],
        )
