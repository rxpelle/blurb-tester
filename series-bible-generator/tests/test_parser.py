"""Tests for bible file parser."""

import pytest
from series_bible_generator.parser import (
    find_bible_files, parse_bible_file, parse_all_bible_files,
    file_checksum, _extract_title, _extract_sections,
    _parse_year, _parse_bloodline_characters, _parse_timeline_events,
    _parse_terminology, _parse_keys,
)
from series_bible_generator.config import Config


class TestFindBibleFiles:
    def test_finds_all_files(self, sample_bible_dir):
        files = find_bible_files(sample_bible_dir)
        assert "bloodline" in files
        assert "timeline" in files
        assert "terminology" in files
        assert "keys" in files

    def test_empty_dir(self, tmp_dir):
        files = find_bible_files(tmp_dir)
        assert len(files) == 0

    def test_custom_prefix(self, tmp_dir):
        (tmp_dir / "CUSTOM_bloodline_tracker.md").write_text("test")
        files = find_bible_files(tmp_dir, prefix="CUSTOM_")
        assert "bloodline" in files


class TestFileChecksum:
    def test_checksum_consistent(self, sample_bloodline_md):
        c1 = file_checksum(sample_bloodline_md)
        c2 = file_checksum(sample_bloodline_md)
        assert c1 == c2

    def test_checksum_changes(self, tmp_dir):
        f = tmp_dir / "test.md"
        f.write_text("version 1")
        c1 = file_checksum(f)
        f.write_text("version 2")
        c2 = file_checksum(f)
        assert c1 != c2


class TestExtractTitle:
    def test_h1_title(self):
        assert _extract_title("# My Title\nContent") == "My Title"

    def test_h2_title(self):
        assert _extract_title("## Sub Title\nContent") == "Sub Title"

    def test_no_title(self):
        assert _extract_title("Just text") == ""


class TestExtractSections:
    def test_basic_sections(self):
        content = "## Section 1\nContent 1\n## Section 2\nContent 2"
        sections = _extract_sections(content)
        assert len(sections) == 2
        assert sections[0][0] == "Section 1"
        assert "Content 1" in sections[0][1]

    def test_nested_sections(self):
        content = "## Top\nText\n### Sub\nMore text"
        sections = _extract_sections(content)
        assert len(sections) == 2


class TestParseYear:
    def test_bce(self):
        assert _parse_year("1189 BCE") == -1189

    def test_ce(self):
        assert _parse_year("28 CE") == 28

    def test_range(self):
        assert _parse_year("1189-1100 BCE") == -1189

    def test_range_with_dash(self):
        assert _parse_year("1189–1100 BCE") == -1189

    def test_invalid(self):
        assert _parse_year("no date here") is None


class TestParseBloodlineCharacters:
    def test_extracts_characters(self, sample_bloodline_md):
        content = sample_bloodline_md.read_text()
        chars = _parse_bloodline_characters(content, str(sample_bloodline_md))
        assert len(chars) >= 2
        names = [c.name for c in chars]
        assert "Pharaoh Tausret" in names

    def test_generation_numbers(self, sample_bloodline_md):
        content = sample_bloodline_md.read_text()
        chars = _parse_bloodline_characters(content, str(sample_bloodline_md))
        tausret = [c for c in chars if "Tausret" in c.name][0]
        assert tausret.generation_absolute == 1

    def test_jesus_generation(self, sample_bloodline_md):
        content = sample_bloodline_md.read_text()
        chars = _parse_bloodline_characters(content, str(sample_bloodline_md))
        jesus = [c for c in chars if "Jesus" in c.name]
        assert len(jesus) == 1
        assert jesus[0].generation_absolute == 42


class TestParseTimelineEvents:
    def test_extracts_events(self, sample_timeline_md):
        content = sample_timeline_md.read_text()
        events = _parse_timeline_events(content, str(sample_timeline_md))
        assert len(events) >= 2

    def test_event_dates(self, sample_timeline_md):
        content = sample_timeline_md.read_text()
        events = _parse_timeline_events(content, str(sample_timeline_md))
        dates = [e.date for e in events]
        assert "1189 BCE" in dates

    def test_event_locations(self, sample_timeline_md):
        content = sample_timeline_md.read_text()
        events = _parse_timeline_events(content, str(sample_timeline_md))
        event_1189 = [e for e in events if e.date == "1189 BCE"][0]
        assert "Egypt" in event_1189.location or "Pi-Ramesses" in event_1189.location


class TestParseTerminology:
    def test_extracts_terms(self, sample_terminology_md):
        content = sample_terminology_md.read_text()
        terms = _parse_terminology(content, str(sample_terminology_md))
        assert len(terms) >= 2
        term_names = [t.term for t in terms]
        assert "Genesis Protocol" in term_names

    def test_incorrect_forms(self, sample_terminology_md):
        content = sample_terminology_md.read_text()
        terms = _parse_terminology(content, str(sample_terminology_md))
        gp = [t for t in terms if t.term == "Genesis Protocol"][0]
        assert "genesis program" in gp.incorrect_forms

    def test_definitions(self, sample_terminology_md):
        content = sample_terminology_md.read_text()
        terms = _parse_terminology(content, str(sample_terminology_md))
        gp = [t for t in terms if t.term == "Genesis Protocol"][0]
        assert "Genetic memory" in gp.definition


class TestParseKeys:
    def test_extracts_keys(self, sample_keys_md):
        content = sample_keys_md.read_text()
        artifacts = _parse_keys(content, str(sample_keys_md))
        assert len(artifacts) >= 2

    def test_key_types(self, sample_keys_md):
        content = sample_keys_md.read_text()
        artifacts = _parse_keys(content, str(sample_keys_md))
        defensive = [a for a in artifacts if a.properties.get("alignment") == "defensive"]
        offensive = [a for a in artifacts if a.properties.get("alignment") == "offensive"]
        assert len(defensive) >= 1
        assert len(offensive) >= 1

    def test_key_descriptions(self, sample_keys_md):
        content = sample_keys_md.read_text()
        artifacts = _parse_keys(content, str(sample_keys_md))
        living_key = [a for a in artifacts if "Living" in a.name][0]
        assert "cipher" in living_key.description.lower() or "authentication" in living_key.description.lower()


class TestParseBibleFile:
    def test_parse_bloodline(self, sample_bloodline_md):
        doc = parse_bible_file(sample_bloodline_md, "bloodline")
        assert doc.doc_type == "bloodline"
        assert len(doc.characters) >= 2
        assert doc.title != ""

    def test_parse_timeline(self, sample_timeline_md):
        doc = parse_bible_file(sample_timeline_md, "timeline")
        assert doc.doc_type == "timeline"
        assert len(doc.events) >= 2

    def test_parse_terminology(self, sample_terminology_md):
        doc = parse_bible_file(sample_terminology_md, "terminology")
        assert len(doc.terms) >= 2

    def test_parse_keys(self, sample_keys_md):
        doc = parse_bible_file(sample_keys_md, "keys")
        assert len(doc.artifacts) >= 2


class TestParseAllBibleFiles:
    def test_parse_all(self, sample_bible_dir, config):
        docs = parse_all_bible_files(sample_bible_dir, config)
        assert len(docs) >= 4
        doc_types = [d.doc_type for d in docs]
        assert "bloodline" in doc_types
        assert "timeline" in doc_types
