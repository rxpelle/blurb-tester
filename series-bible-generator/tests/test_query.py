"""Tests for query module."""

import pytest
from series_bible_generator.query import query_database, get_stats, query_bible_files
from series_bible_generator.db import (
    get_connection, CharacterRepository, EventRepository,
    TermRepository, ArtifactRepository, LocationRepository,
)
from series_bible_generator.models import (
    Character, TimelineEvent, GlossaryTerm, Artifact, Location,
)


@pytest.fixture
def populated_db(config):
    """Database with sample data."""
    conn = get_connection(config)
    CharacterRepository(conn).upsert(
        Character(name="Nefertari", description="Physician", network="defensive",
                 generation_absolute=1, source_file="bloodline.md")
    )
    CharacterRepository(conn).upsert(
        Character(name="Amenhotep", description="Scholar", network="offensive",
                 source_file="bloodline.md")
    )
    EventRepository(conn).add(
        TimelineEvent(date="1189 BCE", year_numeric=-1189,
                     description="Bronze Age Collapse", source_file="timeline.md")
    )
    TermRepository(conn).upsert(
        GlossaryTerm(term="Genesis Protocol", definition="Memory encoding system",
                    source_file="glossary.md")
    )
    ArtifactRepository(conn).upsert(
        Artifact(name="The Living Key", description="Blood cipher",
                source_file="keys.md")
    )
    LocationRepository(conn).add(
        Location(name="Pi-Ramesses", description="Egyptian capital",
                source_file="timeline.md")
    )
    conn.close()
    return config


class TestQueryDatabase:
    def test_search_character(self, populated_db):
        result = query_database("Nefertari", populated_db)
        assert len(result.results) >= 1
        char_results = [r for r in result.results if r["type"] == "character"]
        assert len(char_results) == 1
        assert char_results[0]["name"] == "Nefertari"

    def test_search_event(self, populated_db):
        result = query_database("Bronze", populated_db)
        event_results = [r for r in result.results if r["type"] == "event"]
        assert len(event_results) == 1

    def test_search_term(self, populated_db):
        result = query_database("Genesis", populated_db)
        term_results = [r for r in result.results if r["type"] == "term"]
        assert len(term_results) == 1

    def test_search_artifact(self, populated_db):
        result = query_database("Living", populated_db)
        artifact_results = [r for r in result.results if r["type"] == "artifact"]
        assert len(artifact_results) == 1

    def test_search_location(self, populated_db):
        result = query_database("Ramesses", populated_db)
        loc_results = [r for r in result.results if r["type"] == "location"]
        assert len(loc_results) == 1

    def test_search_no_results(self, populated_db):
        result = query_database("XXXXXXXXX", populated_db)
        assert len(result.results) == 0

    def test_result_type_character(self, populated_db):
        result = query_database("Nefertari", populated_db)
        assert result.result_type == "character"

    def test_sources_tracked(self, populated_db):
        result = query_database("Nefertari", populated_db)
        assert len(result.sources) >= 1


class TestGetStats:
    def test_empty_db(self, config_with_db):
        stats = get_stats(config_with_db)
        assert stats["total"] == 0
        assert stats["characters"] == 0

    def test_with_data(self, populated_db):
        stats = get_stats(populated_db)
        assert stats["characters"] == 2
        assert stats["events"] == 1
        assert stats["terms"] == 1
        assert stats["artifacts"] == 1
        assert stats["locations"] == 1
        assert stats["total"] == 6


class TestQueryBibleFiles:
    def test_searches_files(self, sample_bible_dir, config):
        result = query_bible_files("Nefertari", sample_bible_dir, config)
        assert len(result.results) >= 1

    def test_no_match(self, sample_bible_dir, config):
        result = query_bible_files("XXXXXXXXX", sample_bible_dir, config)
        assert result.context == "No matching content found in bible files."
