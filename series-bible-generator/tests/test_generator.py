"""Tests for bible entry generator."""

import pytest
from series_bible_generator.generator import (
    _generate_without_ai, _format_extraction_data,
    generate_compliance_markdown,
)
from series_bible_generator.models import (
    Character, TimelineEvent, GlossaryTerm, ExtractionResult,
    ComplianceReport, ValidationIssue,
)


class TestGenerateWithoutAI:
    def test_generates_character_section(self):
        extraction = ExtractionResult(manuscript_path="test")
        extraction.characters = [
            Character(name="Nefertari", description="Physician", role="protagonist", network="defensive"),
            Character(name="Amenhotep", description="Scholar", role="antagonist"),
        ]
        result = _generate_without_ai("character_index", extraction)
        assert "Nefertari" in result
        assert "Amenhotep" in result
        assert "Physician" in result

    def test_generates_timeline_section(self):
        extraction = ExtractionResult(manuscript_path="test")
        extraction.events = [
            TimelineEvent(date="1189 BCE", year_numeric=-1189, description="Collapse"),
            TimelineEvent(date="28 CE", year_numeric=28, description="Jesus"),
        ]
        result = _generate_without_ai("timeline", extraction)
        assert "1189 BCE" in result
        assert "28 CE" in result

    def test_generates_terminology_section(self):
        extraction = ExtractionResult(manuscript_path="test")
        extraction.terms = [
            GlossaryTerm(term="Genesis Protocol", definition="Memory system"),
        ]
        result = _generate_without_ai("terminology", extraction)
        assert "Genesis Protocol" in result

    def test_empty_extraction(self):
        extraction = ExtractionResult(manuscript_path="test")
        result = _generate_without_ai("character_index", extraction)
        assert "Series Bible Entry" in result


class TestFormatExtractionData:
    def test_formats_characters(self):
        extraction = ExtractionResult(manuscript_path="test")
        extraction.characters = [
            Character(name="Nefertari", role="protagonist", description="Physician"),
        ]
        result = _format_extraction_data(extraction)
        assert "CHARACTERS:" in result
        assert "Nefertari" in result

    def test_formats_events(self):
        extraction = ExtractionResult(manuscript_path="test")
        extraction.events = [
            TimelineEvent(date="1189 BCE", description="Collapse"),
        ]
        result = _format_extraction_data(extraction)
        assert "TIMELINE EVENTS:" in result

    def test_empty_extraction(self):
        extraction = ExtractionResult(manuscript_path="test")
        result = _format_extraction_data(extraction)
        assert "no data" in result


class TestGenerateComplianceMarkdown:
    def test_basic_report(self):
        report = ComplianceReport(
            manuscript_path="/test/ms",
            bible_path="/test/bible",
            score=95.0,
            total_checks=20,
            passed_checks=19,
        )
        md = generate_compliance_markdown(report)
        assert "95.0/100" in md
        assert "COMPLIANCE REPORT" in md

    def test_report_with_issues(self):
        report = ComplianceReport(
            manuscript_path="/test", bible_path="/test",
            score=80.0, total_checks=10, passed_checks=8,
        )
        report.issues = [
            ValidationIssue(
                severity="error", category="character",
                description="Wrong generation", location="Ch 1",
                suggestion="Fix to Gen 42",
            ),
            ValidationIssue(
                severity="warning", category="terminology",
                description="Wrong term", location="Ch 2",
            ),
        ]
        md = generate_compliance_markdown(report)
        assert "Errors" in md
        assert "Wrong generation" in md
        assert "Warnings" in md

    def test_report_with_chapters(self):
        report = ComplianceReport(
            manuscript_path="/test", bible_path="/test",
        )
        report.chapters_validated = ["chapter_01", "chapter_02"]
        md = generate_compliance_markdown(report)
        assert "chapter_01" in md
        assert "chapter_02" in md
