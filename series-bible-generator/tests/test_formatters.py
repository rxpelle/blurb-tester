"""Tests for formatters."""

import pytest
from io import StringIO
from rich.console import Console

from series_bible_generator.formatters import (
    format_compliance_rich, format_extraction_rich,
    format_query_rich, format_stats_rich,
    format_compliance_text, format_extraction_text,
)
from series_bible_generator.models import (
    ComplianceReport, ValidationIssue, ExtractionResult,
    QueryResult, Character, TimelineEvent, GlossaryTerm,
)


def make_console():
    """Create a console that captures output."""
    return Console(file=StringIO(), force_terminal=True)


class TestFormatComplianceRich:
    def test_displays_score(self):
        console = make_console()
        report = ComplianceReport(
            manuscript_path="/test", bible_path="/test",
            score=95.0, total_checks=20, passed_checks=19,
        )
        format_compliance_rich(report, console=console)
        output = console.file.getvalue()
        assert "95.0" in output

    def test_displays_issues(self):
        console = make_console()
        report = ComplianceReport(
            manuscript_path="/test", bible_path="/test",
        )
        report.issues = [
            ValidationIssue(
                severity="error", category="character",
                description="Wrong generation", location="Ch 1",
            ),
        ]
        format_compliance_rich(report, console=console)
        output = console.file.getvalue()
        assert "Wrong generation" in output

    def test_severity_filter(self):
        console = make_console()
        report = ComplianceReport(
            manuscript_path="/test", bible_path="/test",
        )
        report.issues = [
            ValidationIssue(severity="info", category="continuity",
                          description="Info item", location="ch1"),
            ValidationIssue(severity="error", category="character",
                          description="Error item", location="ch1"),
        ]
        format_compliance_rich(report, min_severity="error", console=console)
        output = console.file.getvalue()
        assert "Error item" in output

    def test_no_issues(self):
        console = make_console()
        report = ComplianceReport(
            manuscript_path="/test", bible_path="/test",
            score=100.0,
        )
        format_compliance_rich(report, console=console)
        output = console.file.getvalue()
        assert "No issues" in output


class TestFormatExtractionRich:
    def test_displays_entities(self):
        console = make_console()
        result = ExtractionResult(manuscript_path="test", chapters_processed=2)
        result.characters = [
            Character(name="Nefertari", role="protagonist", description="Physician"),
        ]
        result.events = [
            TimelineEvent(date="1189 BCE", description="Collapse", significance="major"),
        ]
        format_extraction_rich(result, console=console)
        output = console.file.getvalue()
        assert "Nefertari" in output
        assert "1189 BCE" in output

    def test_empty_result(self):
        console = make_console()
        result = ExtractionResult(manuscript_path="test")
        format_extraction_rich(result, console=console)
        output = console.file.getvalue()
        assert "0" in output


class TestFormatQueryRich:
    def test_displays_character_results(self):
        console = make_console()
        result = QueryResult(
            query="Nefertari",
            result_type="character",
            results=[{
                "type": "character",
                "name": "Nefertari",
                "description": "Physician",
                "network": "defensive",
                "generation": 1,
            }],
        )
        format_query_rich(result, console=console)
        output = console.file.getvalue()
        assert "Nefertari" in output

    def test_displays_ai_answer(self):
        console = make_console()
        result = QueryResult(
            query="test",
            result_type="general",
            results=[{"type": "answer", "content": "AI generated answer here."}],
        )
        format_query_rich(result, console=console)
        output = console.file.getvalue()
        assert "AI generated answer" in output

    def test_no_results(self):
        console = make_console()
        result = QueryResult(query="nothing", result_type="general")
        format_query_rich(result, console=console)
        output = console.file.getvalue()
        assert "0" in output


class TestFormatStatsRich:
    def test_displays_stats(self):
        console = make_console()
        stats = {
            "characters": 10,
            "events": 25,
            "terms": 15,
            "artifacts": 7,
            "locations": 12,
            "total": 69,
            "bible_files_ingested": 4,
            "ingested_files": [],
        }
        format_stats_rich(stats, console=console)
        output = console.file.getvalue()
        assert "69" in output

    def test_no_ingested_files(self):
        console = make_console()
        stats = {
            "characters": 0, "events": 0, "terms": 0,
            "artifacts": 0, "locations": 0, "total": 0,
            "bible_files_ingested": 0, "ingested_files": [],
        }
        format_stats_rich(stats, console=console)
        output = console.file.getvalue()
        assert "ingest" in output.lower()


class TestFormatComplianceText:
    def test_generates_markdown(self):
        report = ComplianceReport(
            manuscript_path="/test", bible_path="/test",
            score=90.0, total_checks=10, passed_checks=9,
        )
        text = format_compliance_text(report)
        assert "COMPLIANCE REPORT" in text
        assert "90.0" in text


class TestFormatExtractionText:
    def test_generates_text(self):
        result = ExtractionResult(manuscript_path="test", chapters_processed=1)
        result.characters = [Character(name="Test", role="protagonist", description="A character")]
        text = format_extraction_text(result)
        assert "Test" in text
        assert "Characters:" in text
