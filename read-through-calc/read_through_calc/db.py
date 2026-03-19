import sqlite3
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from .models import BookInfo


class ReadOnlyDB:
    """Read-only connection to the shared book-data database."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        self.conn.close()

    def get_series_names(self) -> List[str]:
        """Get all distinct series names that have books with positions."""
        rows = self.conn.execute(
            """SELECT DISTINCT series_name FROM books
               WHERE series_name IS NOT NULL AND series_name != ''
               AND series_position IS NOT NULL
               ORDER BY series_name"""
        ).fetchall()
        return [r['series_name'] for r in rows]

    def get_series_books(self, series_name: str) -> List[BookInfo]:
        """Get books in a series ordered by position."""
        rows = self.conn.execute(
            """SELECT id, asin, title, series_name, series_position, kenp_baseline
               FROM books
               WHERE series_name = ? AND series_position IS NOT NULL
               ORDER BY series_position ASC""",
            (series_name,),
        ).fetchall()
        return [BookInfo(
            id=r['id'], asin=r['asin'], title=r['title'],
            series_name=r['series_name'], series_position=r['series_position'],
            kenp_baseline=r['kenp_baseline'],
        ) for r in rows]

    def get_total_units(self, book_id: int) -> int:
        """Get total units sold for a book."""
        row = self.conn.execute(
            "SELECT COALESCE(SUM(units), 0) as total FROM sales WHERE book_id = ?",
            (book_id,),
        ).fetchone()
        return row['total']

    def get_avg_royalty_per_unit(self, book_id: int) -> float:
        """Get average royalty per unit sold."""
        row = self.conn.execute(
            """SELECT COALESCE(SUM(royalty_amount), 0) as total_royalty,
                      COALESCE(SUM(units), 0) as total_units
               FROM sales WHERE book_id = ?""",
            (book_id,),
        ).fetchone()
        if row['total_units'] == 0:
            return 0.0
        return row['total_royalty'] / row['total_units']

    def get_monthly_units(self, book_id: int) -> List[Dict]:
        """Get units sold grouped by month."""
        rows = self.conn.execute(
            """SELECT strftime('%Y-%m', date) as month,
                      SUM(units) as units
               FROM sales WHERE book_id = ?
               GROUP BY strftime('%Y-%m', date)
               ORDER BY month ASC""",
            (book_id,),
        ).fetchall()
        return [{'month': r['month'], 'units': r['units']} for r in rows]

    def get_units_in_window(self, book_id: int, start_date: str, end_date: str) -> int:
        """Get units sold within a date window."""
        row = self.conn.execute(
            """SELECT COALESCE(SUM(units), 0) as total
               FROM sales WHERE book_id = ? AND date >= ? AND date <= ?""",
            (book_id, start_date, end_date),
        ).fetchone()
        return row['total']

    def get_latest_price(self, book_id: int) -> Optional[float]:
        """Get latest price from snapshots."""
        row = self.conn.execute(
            """SELECT price FROM snapshots
               WHERE book_id = ? AND price IS NOT NULL
               ORDER BY timestamp DESC LIMIT 1""",
            (book_id,),
        ).fetchone()
        return row['price'] if row else None
