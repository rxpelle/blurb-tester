"""Tests for database layer."""

import json

import pytest
from series_bible_generator.db import (
    get_connection, CharacterRepository, EventRepository,
    TermRepository, ArtifactRepository, LocationRepository,
    ReportRepository, BibleFileRepository,
)
from series_bible_generator.models import (
    Character, TimelineEvent, GlossaryTerm, Artifact,
    Location, ComplianceReport, ValidationIssue,
)


@pytest.fixture
def conn(config):
    """Get a database connection."""
    c = get_connection(config)
    yield c
    c.close()


class TestGetConnection:
    def test_creates_data_dir(self, config):
        assert not config.data_dir.exists()
        conn = get_connection(config)
        assert config.data_dir.exists()
        conn.close()

    def test_creates_tables(self, conn):
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t["name"] for t in tables}
        assert "characters" in table_names
        assert "timeline_events" in table_names
        assert "glossary_terms" in table_names
        assert "artifacts" in table_names
        assert "locations" in table_names
        assert "compliance_reports" in table_names
        assert "bible_files" in table_names


class TestCharacterRepository:
    def test_upsert_insert(self, conn):
        repo = CharacterRepository(conn)
        char = Character(name="Nefertari", description="Physician", network="defensive")
        id_ = repo.upsert(char)
        assert id_ > 0

    def test_upsert_update(self, conn):
        repo = CharacterRepository(conn)
        repo.upsert(Character(name="Nefertari", description="Old"))
        repo.upsert(Character(name="Nefertari", description="Updated"))
        result = repo.find_by_name("Nefertari")
        assert result["description"] == "Updated"

    def test_find_by_name(self, conn):
        repo = CharacterRepository(conn)
        repo.upsert(Character(name="Sarah Chen", generation_absolute=112))
        result = repo.find_by_name("Sarah Chen")
        assert result is not None
        assert result["generation_absolute"] == 112

    def test_find_by_name_not_found(self, conn):
        repo = CharacterRepository(conn)
        assert repo.find_by_name("Nobody") is None

    def test_search(self, conn):
        repo = CharacterRepository(conn)
        repo.upsert(Character(name="Nefertari"))
        repo.upsert(Character(name="Amenhotep"))
        results = repo.search("Nefer")
        assert len(results) == 1
        assert results[0]["name"] == "Nefertari"

    def test_search_aliases(self, conn):
        repo = CharacterRepository(conn)
        repo.upsert(Character(name="Jesus", aliases=["Yeshua"]))
        results = repo.search("Yeshua")
        assert len(results) == 1

    def test_get_all(self, conn):
        repo = CharacterRepository(conn)
        repo.upsert(Character(name="A"))
        repo.upsert(Character(name="B"))
        assert len(repo.get_all()) == 2

    def test_get_by_network(self, conn):
        repo = CharacterRepository(conn)
        repo.upsert(Character(name="Nefertari", network="defensive"))
        repo.upsert(Character(name="Amenhotep", network="offensive"))
        defensive = repo.get_by_network("defensive")
        assert len(defensive) == 1
        assert defensive[0]["name"] == "Nefertari"

    def test_get_by_book(self, conn):
        repo = CharacterRepository(conn)
        repo.upsert(Character(name="Thomas", first_appearance_book="Book 1"))
        repo.upsert(Character(name="Sarah", first_appearance_book="Book 2"))
        results = repo.get_by_book("Book 1")
        assert len(results) == 1

    def test_count(self, conn):
        repo = CharacterRepository(conn)
        assert repo.count() == 0
        repo.upsert(Character(name="Test"))
        assert repo.count() == 1

    def test_delete_by_source(self, conn):
        repo = CharacterRepository(conn)
        repo.upsert(Character(name="A", source_file="file1.md"))
        repo.upsert(Character(name="B", source_file="file2.md"))
        repo.delete_by_source("file1.md")
        assert repo.count() == 1
        assert repo.find_by_name("B") is not None


class TestEventRepository:
    def test_add(self, conn):
        repo = EventRepository(conn)
        event = TimelineEvent(date="1189 BCE", year_numeric=-1189, description="Collapse")
        id_ = repo.add(event)
        assert id_ > 0

    def test_search(self, conn):
        repo = EventRepository(conn)
        repo.add(TimelineEvent(date="1189 BCE", description="Bronze Age Collapse"))
        repo.add(TimelineEvent(date="1347 CE", description="Black Death"))
        results = repo.search("Bronze")
        assert len(results) == 1

    def test_get_by_era(self, conn):
        repo = EventRepository(conn)
        repo.add(TimelineEvent(date="1189 BCE", year_numeric=-1189))
        repo.add(TimelineEvent(date="28 CE", year_numeric=28))
        repo.add(TimelineEvent(date="1347 CE", year_numeric=1347))
        results = repo.get_by_era(-1200, 0)
        assert len(results) == 1

    def test_get_by_book(self, conn):
        repo = EventRepository(conn)
        repo.add(TimelineEvent(date="test", book="Book 3"))
        repo.add(TimelineEvent(date="test", book="Book 1"))
        results = repo.get_by_book("Book 3")
        assert len(results) == 1

    def test_count(self, conn):
        repo = EventRepository(conn)
        assert repo.count() == 0


class TestTermRepository:
    def test_upsert_insert(self, conn):
        repo = TermRepository(conn)
        term = GlossaryTerm(term="Genesis Protocol", definition="Memory encoding")
        id_ = repo.upsert(term)
        assert id_ > 0

    def test_upsert_update(self, conn):
        repo = TermRepository(conn)
        repo.upsert(GlossaryTerm(term="Test", definition="Old"))
        repo.upsert(GlossaryTerm(term="Test", definition="New"))
        result = repo.find_by_term("Test")
        assert result["definition"] == "New"

    def test_search(self, conn):
        repo = TermRepository(conn)
        repo.upsert(GlossaryTerm(term="Genesis Protocol"))
        repo.upsert(GlossaryTerm(term="The Order"))
        results = repo.search("Genesis")
        assert len(results) == 1

    def test_get_all(self, conn):
        repo = TermRepository(conn)
        repo.upsert(GlossaryTerm(term="A"))
        repo.upsert(GlossaryTerm(term="B"))
        assert len(repo.get_all()) == 2


class TestArtifactRepository:
    def test_upsert(self, conn):
        repo = ArtifactRepository(conn)
        a = Artifact(name="Key 1", artifact_type="key")
        id_ = repo.upsert(a)
        assert id_ > 0

    def test_search(self, conn):
        repo = ArtifactRepository(conn)
        repo.upsert(Artifact(name="The Living Key", description="Blood cipher"))
        results = repo.search("Living")
        assert len(results) == 1

    def test_upsert_update(self, conn):
        repo = ArtifactRepository(conn)
        repo.upsert(Artifact(name="Key 1", description="Old"))
        repo.upsert(Artifact(name="Key 1", description="Updated"))
        result = repo.find_by_name("Key 1")
        assert result["description"] == "Updated"


class TestLocationRepository:
    def test_add(self, conn):
        repo = LocationRepository(conn)
        loc = Location(name="Pi-Ramesses", era="Bronze Age")
        id_ = repo.add(loc)
        assert id_ > 0

    def test_search(self, conn):
        repo = LocationRepository(conn)
        repo.add(Location(name="Pi-Ramesses"))
        repo.add(Location(name="Memphis"))
        results = repo.search("Ramesses")
        assert len(results) == 1


class TestReportRepository:
    def test_save_and_get(self, conn):
        repo = ReportRepository(conn)
        report = ComplianceReport(
            manuscript_path="/test/ms",
            bible_path="/test/bible",
            score=95.0,
            total_checks=20,
            passed_checks=19,
        )
        report.add_issue(ValidationIssue(
            severity="warning", category="terminology",
            description="test issue", location="ch1",
        ))
        id_ = repo.save(report)
        assert id_ > 0

        latest = repo.get_latest("/test/ms")
        assert latest is not None
        assert latest["score"] == 95.0

    def test_get_history(self, conn):
        repo = ReportRepository(conn)
        for score in [80.0, 85.0, 90.0]:
            r = ComplianceReport(
                manuscript_path="/test/ms", bible_path="/test/bible", score=score,
            )
            repo.save(r)
        history = repo.get_history("/test/ms")
        assert len(history) == 3


class TestBibleFileRepository:
    def test_record_ingest(self, conn):
        repo = BibleFileRepository(conn)
        repo.record_ingest("/test/bible.md", "timeline", "Master Timeline", "abc123")
        ingested = repo.get_ingested()
        assert len(ingested) == 1
        assert ingested[0]["doc_type"] == "timeline"

    def test_get_checksum(self, conn):
        repo = BibleFileRepository(conn)
        repo.record_ingest("/test/bible.md", "timeline", "Test", "hash123")
        assert repo.get_checksum("/test/bible.md") == "hash123"
        assert repo.get_checksum("/other/path.md") is None

    def test_replace_on_reingest(self, conn):
        repo = BibleFileRepository(conn)
        repo.record_ingest("/test/bible.md", "timeline", "Test", "hash1")
        repo.record_ingest("/test/bible.md", "timeline", "Test", "hash2")
        assert repo.get_checksum("/test/bible.md") == "hash2"
        assert len(repo.get_ingested()) == 1
