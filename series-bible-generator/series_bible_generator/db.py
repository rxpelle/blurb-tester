"""SQLite database layer for series bible entity storage."""

import json
import sqlite3
from pathlib import Path
from typing import Optional

from .config import Config
from .models import (
    Character, TimelineEvent, GlossaryTerm, Artifact,
    Location, ComplianceReport, ValidationIssue,
)


def get_connection(config: Config) -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    config.data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(config.db_path))
    conn.row_factory = sqlite3.Row
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn: sqlite3.Connection):
    """Create tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            aliases TEXT DEFAULT '[]',
            description TEXT DEFAULT '',
            first_appearance_book TEXT DEFAULT '',
            first_appearance_chapter TEXT DEFAULT '',
            era TEXT DEFAULT '',
            generation_absolute INTEGER,
            generation_local INTEGER,
            status TEXT DEFAULT '',
            role TEXT DEFAULT '',
            network TEXT DEFAULT '',
            relationships TEXT DEFAULT '[]',
            traits TEXT DEFAULT '[]',
            locations TEXT DEFAULT '[]',
            source_file TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            year_numeric INTEGER,
            description TEXT DEFAULT '',
            book TEXT DEFAULT '',
            chapter TEXT DEFAULT '',
            era TEXT DEFAULT '',
            characters_involved TEXT DEFAULT '[]',
            location TEXT DEFAULT '',
            significance TEXT DEFAULT '',
            source_file TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS glossary_terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT NOT NULL UNIQUE,
            definition TEXT DEFAULT '',
            correct_usage TEXT DEFAULT '',
            incorrect_forms TEXT DEFAULT '[]',
            era_restrictions TEXT DEFAULT '[]',
            book_specific_notes TEXT DEFAULT '{}',
            source_file TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            artifact_type TEXT DEFAULT '',
            created_date TEXT DEFAULT '',
            created_by TEXT DEFAULT '',
            current_holder TEXT DEFAULT '',
            movement_log TEXT DEFAULT '[]',
            properties TEXT DEFAULT '{}',
            source_file TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            aliases TEXT DEFAULT '[]',
            description TEXT DEFAULT '',
            era TEXT DEFAULT '',
            books_featured TEXT DEFAULT '[]',
            characters_present TEXT DEFAULT '[]',
            source_file TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS compliance_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manuscript_path TEXT NOT NULL,
            bible_path TEXT NOT NULL,
            report_date TEXT NOT NULL,
            score REAL DEFAULT 0.0,
            total_checks INTEGER DEFAULT 0,
            passed_checks INTEGER DEFAULT 0,
            issues TEXT DEFAULT '[]',
            chapters_validated TEXT DEFAULT '[]',
            summary TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS bible_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL UNIQUE,
            doc_type TEXT NOT NULL,
            title TEXT DEFAULT '',
            checksum TEXT DEFAULT '',
            last_ingested TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
        CREATE INDEX IF NOT EXISTS idx_characters_network ON characters(network);
        CREATE INDEX IF NOT EXISTS idx_events_year ON timeline_events(year_numeric);
        CREATE INDEX IF NOT EXISTS idx_events_book ON timeline_events(book);
        CREATE INDEX IF NOT EXISTS idx_terms_term ON glossary_terms(term);
        CREATE INDEX IF NOT EXISTS idx_artifacts_name ON artifacts(name);
    """)
    conn.commit()


class CharacterRepository:
    """CRUD operations for characters."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert(self, char: Character) -> int:
        """Insert or update a character."""
        existing = self.find_by_name(char.name)
        if existing:
            self.conn.execute("""
                UPDATE characters SET
                    aliases=?, description=?, first_appearance_book=?,
                    first_appearance_chapter=?, era=?, generation_absolute=?,
                    generation_local=?, status=?, role=?, network=?,
                    relationships=?, traits=?, locations=?, source_file=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE name=?
            """, (
                json.dumps(char.aliases), char.description,
                char.first_appearance_book, char.first_appearance_chapter,
                char.era, char.generation_absolute, char.generation_local,
                char.status, char.role, char.network,
                json.dumps(char.relationships), json.dumps(char.traits),
                json.dumps(char.locations), char.source_file, char.name,
            ))
            self.conn.commit()
            return existing["id"]
        else:
            cursor = self.conn.execute("""
                INSERT INTO characters (
                    name, aliases, description, first_appearance_book,
                    first_appearance_chapter, era, generation_absolute,
                    generation_local, status, role, network,
                    relationships, traits, locations, source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                char.name, json.dumps(char.aliases), char.description,
                char.first_appearance_book, char.first_appearance_chapter,
                char.era, char.generation_absolute, char.generation_local,
                char.status, char.role, char.network,
                json.dumps(char.relationships), json.dumps(char.traits),
                json.dumps(char.locations), char.source_file,
            ))
            self.conn.commit()
            return cursor.lastrowid

    def find_by_name(self, name: str) -> Optional[dict]:
        """Find a character by exact name."""
        row = self.conn.execute(
            "SELECT * FROM characters WHERE name = ?", (name,)
        ).fetchone()
        return dict(row) if row else None

    def search(self, query: str) -> list:
        """Search characters by name or alias."""
        rows = self.conn.execute(
            "SELECT * FROM characters WHERE name LIKE ? OR aliases LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all(self) -> list:
        """Get all characters."""
        rows = self.conn.execute(
            "SELECT * FROM characters ORDER BY generation_absolute, name"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_by_network(self, network: str) -> list:
        """Get characters by network affiliation."""
        rows = self.conn.execute(
            "SELECT * FROM characters WHERE network = ? ORDER BY name",
            (network,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_by_book(self, book: str) -> list:
        """Get characters appearing in a specific book."""
        rows = self.conn.execute(
            "SELECT * FROM characters WHERE first_appearance_book LIKE ?",
            (f"%{book}%",),
        ).fetchall()
        return [dict(r) for r in rows]

    def count(self) -> int:
        """Count total characters."""
        return self.conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0]

    def delete_by_source(self, source_file: str):
        """Delete all characters from a specific source file."""
        self.conn.execute("DELETE FROM characters WHERE source_file = ?", (source_file,))
        self.conn.commit()


class EventRepository:
    """CRUD operations for timeline events."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, event: TimelineEvent) -> int:
        """Insert a timeline event."""
        cursor = self.conn.execute("""
            INSERT INTO timeline_events (
                date, year_numeric, description, book, chapter,
                era, characters_involved, location, significance, source_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.date, event.year_numeric, event.description,
            event.book, event.chapter, event.era,
            json.dumps(event.characters_involved), event.location,
            event.significance, event.source_file,
        ))
        self.conn.commit()
        return cursor.lastrowid

    def search(self, query: str) -> list:
        """Search events by description or characters."""
        rows = self.conn.execute(
            "SELECT * FROM timeline_events WHERE description LIKE ? OR characters_involved LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_by_era(self, year_start: int, year_end: int) -> list:
        """Get events in a year range."""
        rows = self.conn.execute(
            "SELECT * FROM timeline_events WHERE year_numeric BETWEEN ? AND ? ORDER BY year_numeric",
            (year_start, year_end),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_by_book(self, book: str) -> list:
        """Get events for a specific book."""
        rows = self.conn.execute(
            "SELECT * FROM timeline_events WHERE book LIKE ? ORDER BY year_numeric",
            (f"%{book}%",),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all(self) -> list:
        """Get all events ordered by year."""
        rows = self.conn.execute(
            "SELECT * FROM timeline_events ORDER BY year_numeric"
        ).fetchall()
        return [dict(r) for r in rows]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM timeline_events").fetchone()[0]

    def delete_by_source(self, source_file: str):
        self.conn.execute("DELETE FROM timeline_events WHERE source_file = ?", (source_file,))
        self.conn.commit()


class TermRepository:
    """CRUD operations for glossary terms."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert(self, term: GlossaryTerm) -> int:
        """Insert or update a glossary term."""
        existing = self.find_by_term(term.term)
        if existing:
            self.conn.execute("""
                UPDATE glossary_terms SET
                    definition=?, correct_usage=?, incorrect_forms=?,
                    era_restrictions=?, book_specific_notes=?, source_file=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE term=?
            """, (
                term.definition, term.correct_usage,
                json.dumps(term.incorrect_forms),
                json.dumps(term.era_restrictions),
                json.dumps(term.book_specific_notes),
                term.source_file, term.term,
            ))
            self.conn.commit()
            return existing["id"]
        else:
            cursor = self.conn.execute("""
                INSERT INTO glossary_terms (
                    term, definition, correct_usage, incorrect_forms,
                    era_restrictions, book_specific_notes, source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                term.term, term.definition, term.correct_usage,
                json.dumps(term.incorrect_forms),
                json.dumps(term.era_restrictions),
                json.dumps(term.book_specific_notes),
                term.source_file,
            ))
            self.conn.commit()
            return cursor.lastrowid

    def find_by_term(self, term: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM glossary_terms WHERE term = ?", (term,)
        ).fetchone()
        return dict(row) if row else None

    def search(self, query: str) -> list:
        rows = self.conn.execute(
            "SELECT * FROM glossary_terms WHERE term LIKE ? OR definition LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all(self) -> list:
        rows = self.conn.execute(
            "SELECT * FROM glossary_terms ORDER BY term"
        ).fetchall()
        return [dict(r) for r in rows]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM glossary_terms").fetchone()[0]

    def delete_by_source(self, source_file: str):
        self.conn.execute("DELETE FROM glossary_terms WHERE source_file = ?", (source_file,))
        self.conn.commit()


class ArtifactRepository:
    """CRUD operations for artifacts."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert(self, artifact: Artifact) -> int:
        existing = self.find_by_name(artifact.name)
        if existing:
            self.conn.execute("""
                UPDATE artifacts SET
                    description=?, artifact_type=?, created_date=?,
                    created_by=?, current_holder=?, movement_log=?,
                    properties=?, source_file=?, updated_at=CURRENT_TIMESTAMP
                WHERE name=?
            """, (
                artifact.description, artifact.artifact_type,
                artifact.created_date, artifact.created_by,
                artifact.current_holder, json.dumps(artifact.movement_log),
                json.dumps(artifact.properties), artifact.source_file,
                artifact.name,
            ))
            self.conn.commit()
            return existing["id"]
        else:
            cursor = self.conn.execute("""
                INSERT INTO artifacts (
                    name, description, artifact_type, created_date,
                    created_by, current_holder, movement_log, properties, source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                artifact.name, artifact.description, artifact.artifact_type,
                artifact.created_date, artifact.created_by,
                artifact.current_holder, json.dumps(artifact.movement_log),
                json.dumps(artifact.properties), artifact.source_file,
            ))
            self.conn.commit()
            return cursor.lastrowid

    def find_by_name(self, name: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM artifacts WHERE name = ?", (name,)
        ).fetchone()
        return dict(row) if row else None

    def search(self, query: str) -> list:
        rows = self.conn.execute(
            "SELECT * FROM artifacts WHERE name LIKE ? OR description LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all(self) -> list:
        rows = self.conn.execute("SELECT * FROM artifacts ORDER BY name").fetchall()
        return [dict(r) for r in rows]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0]

    def delete_by_source(self, source_file: str):
        self.conn.execute("DELETE FROM artifacts WHERE source_file = ?", (source_file,))
        self.conn.commit()


class LocationRepository:
    """CRUD operations for locations."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, location: Location) -> int:
        cursor = self.conn.execute("""
            INSERT INTO locations (
                name, aliases, description, era,
                books_featured, characters_present, source_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            location.name, json.dumps(location.aliases),
            location.description, location.era,
            json.dumps(location.books_featured),
            json.dumps(location.characters_present),
            location.source_file,
        ))
        self.conn.commit()
        return cursor.lastrowid

    def search(self, query: str) -> list:
        rows = self.conn.execute(
            "SELECT * FROM locations WHERE name LIKE ? OR aliases LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all(self) -> list:
        rows = self.conn.execute("SELECT * FROM locations ORDER BY name").fetchall()
        return [dict(r) for r in rows]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0]

    def delete_by_source(self, source_file: str):
        self.conn.execute("DELETE FROM locations WHERE source_file = ?", (source_file,))
        self.conn.commit()


class ReportRepository:
    """CRUD operations for compliance reports."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, report: ComplianceReport) -> int:
        issues_data = [
            {
                "severity": i.severity,
                "category": i.category,
                "description": i.description,
                "location": i.location,
                "bible_reference": i.bible_reference,
                "suggestion": i.suggestion,
            }
            for i in report.issues
        ]
        cursor = self.conn.execute("""
            INSERT INTO compliance_reports (
                manuscript_path, bible_path, report_date, score,
                total_checks, passed_checks, issues,
                chapters_validated, summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report.manuscript_path, report.bible_path,
            report.report_date, report.score,
            report.total_checks, report.passed_checks,
            json.dumps(issues_data),
            json.dumps(report.chapters_validated),
            report.summary,
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_latest(self, manuscript_path: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM compliance_reports WHERE manuscript_path = ? ORDER BY created_at DESC LIMIT 1",
            (manuscript_path,),
        ).fetchone()
        return dict(row) if row else None

    def get_history(self, manuscript_path: str) -> list:
        rows = self.conn.execute(
            "SELECT * FROM compliance_reports WHERE manuscript_path = ? ORDER BY created_at DESC",
            (manuscript_path,),
        ).fetchall()
        return [dict(r) for r in rows]


class BibleFileRepository:
    """Track which bible files have been ingested."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def record_ingest(self, file_path: str, doc_type: str, title: str, checksum: str):
        self.conn.execute("""
            INSERT OR REPLACE INTO bible_files (file_path, doc_type, title, checksum, last_ingested)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (file_path, doc_type, title, checksum))
        self.conn.commit()

    def get_ingested(self) -> list:
        rows = self.conn.execute(
            "SELECT * FROM bible_files ORDER BY doc_type"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_checksum(self, file_path: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT checksum FROM bible_files WHERE file_path = ?", (file_path,)
        ).fetchone()
        return row["checksum"] if row else None
