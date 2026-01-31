import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class Database:
    """Database manager for Copart deal finder."""

    def __init__(self, db_path: str = "data/copart.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.initialize()

    def initialize(self):
        """Create database schema if it doesn't exist."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Vehicles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                lot_number INTEGER PRIMARY KEY,
                vin VARCHAR(17),
                year INTEGER,
                make VARCHAR(50),
                model VARCHAR(100),
                trim VARCHAR(50),
                body_style VARCHAR(50),
                odometer INTEGER,
                odometer_status VARCHAR(20),

                -- Engine/Drivetrain
                engine_type VARCHAR(50),
                transmission VARCHAR(50),
                drivetrain VARCHAR(50),
                fuel_type VARCHAR(30),

                -- Title/Legal
                title_type VARCHAR(30),
                title_code VARCHAR(10),
                title_state VARCHAR(2),

                -- Damage
                primary_damage VARCHAR(50),
                secondary_damage TEXT,
                has_keys BOOLEAN,
                runs_drives BOOLEAN,
                engine_starts BOOLEAN,
                transmission_engages BOOLEAN,

                -- Location/Auction
                location VARCHAR(100),
                sale_date DATETIME,
                sale_type VARCHAR(50),
                seller VARCHAR(100),

                -- Pricing
                current_bid DECIMAL(10,2),
                buy_now_price DECIMAL(10,2),
                estimated_retail_value DECIMAL(10,2),
                reserve_met BOOLEAN,

                -- Quality scores
                autograde_score DECIMAL(2,1),
                autocheck_score INTEGER,

                -- Timestamps
                first_seen DATETIME,
                last_updated DATETIME,

                -- Metadata
                image_urls TEXT,
                detail_page_url TEXT,
                notes TEXT,

                -- Calculated fields
                deal_score DECIMAL(5,2),
                estimated_repair_cost DECIMAL(10,2)
            )
        """)

        # Bid history tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bid_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lot_number INTEGER,
                bid_amount DECIMAL(10,2),
                timestamp DATETIME,
                FOREIGN KEY (lot_number) REFERENCES vehicles(lot_number)
            )
        """)

        # Saved searches
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100),
                criteria TEXT,
                created_at DATETIME
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_date ON vehicles(sale_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deal_score ON vehicles(deal_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_location ON vehicles(location)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_make_model ON vehicles(make, model)")

        self.conn.commit()
        print(f"Database initialized at {self.db_path}")

    def insert_vehicle(self, vehicle_data: Dict[str, Any]) -> bool:
        """Insert or update a vehicle record."""
        try:
            cursor = self.conn.cursor()

            # Check if vehicle exists
            existing = cursor.execute(
                "SELECT lot_number, first_seen FROM vehicles WHERE lot_number = ?",
                (vehicle_data.get('lot_number'),)
            ).fetchone()

            if existing:
                # Update existing record
                vehicle_data['first_seen'] = existing['first_seen']
                vehicle_data['last_updated'] = datetime.now().isoformat()

                # Track bid history if bid changed
                cursor.execute(
                    "INSERT INTO bid_history (lot_number, bid_amount, timestamp) VALUES (?, ?, ?)",
                    (vehicle_data['lot_number'], vehicle_data.get('current_bid', 0), datetime.now().isoformat())
                )
            else:
                # New record
                vehicle_data['first_seen'] = datetime.now().isoformat()
                vehicle_data['last_updated'] = datetime.now().isoformat()

            # Convert lists/dicts to JSON strings
            if 'image_urls' in vehicle_data and isinstance(vehicle_data['image_urls'], list):
                vehicle_data['image_urls'] = json.dumps(vehicle_data['image_urls'])

            # Prepare SQL
            columns = ', '.join(vehicle_data.keys())
            placeholders = ', '.join(['?' for _ in vehicle_data])

            sql = f"INSERT OR REPLACE INTO vehicles ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, list(vehicle_data.values()))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error inserting vehicle: {e}")
            return False

    def get_vehicles(self, filters: Optional[Dict[str, Any]] = None,
                     limit: int = 100, order_by: str = "deal_score DESC") -> List[Dict[str, Any]]:
        """Get vehicles with optional filters."""
        cursor = self.conn.cursor()

        query = "SELECT * FROM vehicles WHERE 1=1"
        params = []

        if filters:
            if 'min_deal_score' in filters:
                query += " AND deal_score >= ?"
                params.append(filters['min_deal_score'])

            if 'location' in filters:
                query += " AND location = ?"
                params.append(filters['location'])

            if 'make' in filters:
                query += " AND make = ?"
                params.append(filters['make'])

            if 'min_year' in filters:
                query += " AND year >= ?"
                params.append(filters['min_year'])

            if 'max_mileage' in filters:
                query += " AND odometer <= ?"
                params.append(filters['max_mileage'])

            if 'upcoming_auction_hours' in filters:
                query += " AND sale_date >= datetime('now') AND sale_date <= datetime('now', '+' || ? || ' hours')"
                params.append(filters['upcoming_auction_hours'])

        query += f" ORDER BY {order_by} LIMIT ?"
        params.append(limit)

        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_top_deals(self, limit: int = 20, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get top deals sorted by score."""
        filters = {'min_deal_score': 50}
        if location:
            filters['location'] = location

        return self.get_vehicles(filters=filters, limit=limit, order_by="deal_score DESC")

    def get_upcoming_auctions(self, hours: int = 12) -> List[Dict[str, Any]]:
        """Get vehicles with auctions in the next X hours."""
        filters = {'upcoming_auction_hours': hours}
        return self.get_vehicles(filters=filters, limit=100, order_by="sale_date ASC")

    def get_vehicle_by_lot(self, lot_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific vehicle by lot number."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM vehicles WHERE lot_number = ?", (lot_number,)).fetchone()
        return dict(row) if row else None

    def get_bid_history(self, lot_number: int) -> List[Dict[str, Any]]:
        """Get bid history for a vehicle."""
        cursor = self.conn.cursor()
        rows = cursor.execute(
            "SELECT * FROM bid_history WHERE lot_number = ? ORDER BY timestamp",
            (lot_number,)
        ).fetchall()
        return [dict(row) for row in rows]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
