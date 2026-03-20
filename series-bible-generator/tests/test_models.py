"""Tests for data models."""

import pytest
from series_bible_generator.models import (
    Character, TimelineEvent, GlossaryTerm, Artifact,
    Location, ValidationIssue, ComplianceReport, ExtractionResult,
    QueryResult, BibleDocument,
)


class TestCharacter:
    def test_create_basic(self):
        c = Character(name="Nefertari")
        assert c.name == "Nefertari"
        assert c.aliases == []
        assert c.generation_absolute is None

    def test_create_full(self):
        c = Character(
            name="Nefertari",
            aliases=["Nefer"],
            description="Physician",
            generation_absolute=1,
            network="defensive",
            role="protagonist",
            status="dead",
        )
        assert c.network == "defensive"
        assert c.generation_absolute == 1
        assert c.all_names == ["Nefertari", "Nefer"]

    def test_invalid_status(self):
        with pytest.raises(ValueError, match="Invalid status"):
            Character(name="Test", status="invalid")

    def test_invalid_role(self):
        with pytest.raises(ValueError, match="Invalid role"):
            Character(name="Test", role="villain")

    def test_all_names(self):
        c = Character(name="Jesus", aliases=["Yeshua", "Jesus of Nazareth"])
        assert c.all_names == ["Jesus", "Yeshua", "Jesus of Nazareth"]

    def test_empty_status_ok(self):
        c = Character(name="Test", status="")
        assert c.status == ""


class TestTimelineEvent:
    def test_create_basic(self):
        e = TimelineEvent(date="1189 BCE")
        assert e.date == "1189 BCE"
        assert e.year_numeric is None

    def test_create_full(self):
        e = TimelineEvent(
            date="1189 BCE",
            year_numeric=-1189,
            description="Bronze Age Collapse",
            significance="major",
        )
        assert e.year_numeric == -1189
        assert e.significance == "major"

    def test_invalid_significance(self):
        with pytest.raises(ValueError, match="Invalid significance"):
            TimelineEvent(date="test", significance="huge")


class TestGlossaryTerm:
    def test_create(self):
        t = GlossaryTerm(
            term="Genesis Protocol",
            definition="Genetic memory encoding system",
            incorrect_forms=["genesis program", "protocol system"],
        )
        assert t.term == "Genesis Protocol"
        assert len(t.incorrect_forms) == 2

    def test_book_specific_notes(self):
        t = GlossaryTerm(
            term="The Order",
            book_specific_notes={"Book 1": "Thomas encounters", "Book 2": "GenVault"},
        )
        assert "Book 1" in t.book_specific_notes


class TestArtifact:
    def test_create(self):
        a = Artifact(
            name="Defensive Key 1",
            artifact_type="key",
            created_by="Nefertari",
        )
        assert a.artifact_type == "key"


class TestLocation:
    def test_create(self):
        loc = Location(
            name="Pi-Ramesses",
            aliases=["Per-Ramesses"],
            era="Bronze Age",
        )
        assert loc.aliases == ["Per-Ramesses"]


class TestValidationIssue:
    def test_create(self):
        i = ValidationIssue(
            severity="error",
            category="character",
            description="Wrong generation number",
            location="Chapter 1",
        )
        assert i.severity == "error"

    def test_invalid_severity(self):
        with pytest.raises(ValueError):
            ValidationIssue(severity="fatal", category="character",
                          description="test", location="test")

    def test_invalid_category(self):
        with pytest.raises(ValueError):
            ValidationIssue(severity="error", category="plot",
                          description="test", location="test")


class TestComplianceReport:
    def test_empty_report(self):
        r = ComplianceReport(manuscript_path="test", bible_path="test")
        r.calculate_score()
        assert r.score == 100.0

    def test_add_issue(self):
        r = ComplianceReport(manuscript_path="test", bible_path="test")
        r.add_issue(ValidationIssue(
            severity="error", category="character",
            description="test", location="ch1",
        ))
        assert r.total_checks == 1
        assert len(r.errors) == 1
        assert len(r.warnings) == 0

    def test_add_pass(self):
        r = ComplianceReport(manuscript_path="test", bible_path="test")
        r.add_pass()
        r.add_pass()
        r.add_issue(ValidationIssue(
            severity="warning", category="terminology",
            description="test", location="ch1",
        ))
        r.calculate_score()
        assert r.total_checks == 3
        assert r.passed_checks == 2
        assert r.score == pytest.approx(66.7, abs=0.1)

    def test_score_with_mixed_issues(self):
        r = ComplianceReport(manuscript_path="test", bible_path="test")
        for _ in range(8):
            r.add_pass()
        r.add_issue(ValidationIssue(
            severity="error", category="character",
            description="test", location="ch1",
        ))
        r.add_issue(ValidationIssue(
            severity="info", category="continuity",
            description="test", location="ch2",
        ))
        r.calculate_score()
        assert r.score == 80.0
        assert len(r.errors) == 1
        assert len(r.info_items) == 1


class TestExtractionResult:
    def test_total_entities(self):
        r = ExtractionResult(manuscript_path="test")
        r.characters = [Character(name="A"), Character(name="B")]
        r.events = [TimelineEvent(date="100 CE")]
        assert r.total_entities == 3

    def test_empty(self):
        r = ExtractionResult(manuscript_path="test")
        assert r.total_entities == 0
        assert r.chapters_processed == 0


class TestQueryResult:
    def test_create(self):
        q = QueryResult(query="Nefertari", result_type="character")
        assert q.query == "Nefertari"
        assert q.results == []


class TestBibleDocument:
    def test_create(self):
        d = BibleDocument(
            doc_type="bloodline",
            title="Bloodline Tracker",
            file_path="/test/path.md",
            content="# test",
        )
        assert d.doc_type == "bloodline"
        assert d.characters == []
