"""Tests for manuscript validator."""

import pytest
from series_bible_generator.validator import (
    _check_structural, _check_terminology, _parse_validation_response,
    _generate_summary, validate_manuscript,
)
from series_bible_generator.db import get_connection, TermRepository
from series_bible_generator.models import (
    ComplianceReport, ValidationIssue, GlossaryTerm,
)
from series_bible_generator.config import Config


class TestCheckStructural:
    def test_no_headings(self, config):
        issues = _check_structural("Just plain text with no headings", "ch1", config)
        assert any(i.category == "continuity" for i in issues)

    def test_short_chapter(self, config):
        issues = _check_structural("Short chapter.", "ch1", config)
        assert any("short" in i.description.lower() for i in issues)

    def test_placeholder_text(self, config):
        issues = _check_structural("# Chapter\nSome text TODO fix later", "ch1", config)
        assert any("TODO" in i.description for i in issues)

    def test_fixme_placeholder(self, config):
        issues = _check_structural("# Chapter\nNeed to FIXME here", "ch1", config)
        assert any("FIXME" in i.description for i in issues)

    def test_tbd_placeholder(self, config):
        issues = _check_structural("# Chapter\nDetails TBD", "ch1", config)
        assert any("TBD" in i.description for i in issues)

    def test_clean_chapter(self, config):
        text = "# Chapter 1\n\n" + "Normal text with enough words to pass the threshold. " * 100
        issues = _check_structural(text, "ch1", config)
        assert len(issues) == 0

    def test_multiple_placeholders(self, config):
        issues = _check_structural("# Ch\nTODO and FIXME and TBD\n" + "word " * 500, "ch1", config)
        placeholder_issues = [i for i in issues if "laceholder" in i.description or
                             i.description.startswith("Placeholder")]
        assert len(placeholder_issues) == 3


class TestCheckTerminology:
    def test_catches_incorrect_form(self, config):
        # Set up terms in database
        conn = get_connection(config)
        TermRepository(conn).upsert(GlossaryTerm(
            term="Genesis Protocol",
            incorrect_forms=["genesis program", "protocol system"],
        ))
        conn.close()

        issues = _check_terminology(
            "The genesis program was activated.", "ch1", config,
        )
        assert len(issues) >= 1
        assert "genesis program" in issues[0].description

    def test_no_issues(self, config):
        conn = get_connection(config)
        TermRepository(conn).upsert(GlossaryTerm(
            term="Genesis Protocol",
            incorrect_forms=["genesis program"],
        ))
        conn.close()

        issues = _check_terminology(
            "The Genesis Protocol was activated.", "ch1", config,
        )
        assert len(issues) == 0

    def test_empty_database(self, config):
        get_connection(config).close()  # ensure tables exist
        issues = _check_terminology("Any text here", "ch1", config)
        assert len(issues) == 0


class TestParseValidationResponse:
    def test_valid_json(self):
        response = """[
            {"severity": "error", "category": "character", "description": "Wrong gen", "location": "Ch 1", "bible_reference": "Bloodline", "suggestion": "Fix it"}
        ]"""
        issues = _parse_validation_response(response)
        assert len(issues) == 1
        assert issues[0].severity == "error"

    def test_empty_array(self):
        issues = _parse_validation_response("[]")
        assert len(issues) == 0

    def test_invalid_json(self):
        issues = _parse_validation_response("not json at all")
        assert len(issues) == 0

    def test_mixed_valid_invalid(self):
        response = """[
            {"severity": "error", "category": "character", "description": "test", "location": "ch1"},
            {"severity": "invalid_sev", "category": "character", "description": "bad", "location": "ch1"}
        ]"""
        issues = _parse_validation_response(response)
        assert len(issues) == 1  # second one skipped due to invalid severity

    def test_json_in_markdown(self):
        response = """Here are the issues:
```json
[{"severity": "warning", "category": "terminology", "description": "test", "location": "ch1"}]
```"""
        issues = _parse_validation_response(response)
        assert len(issues) == 1


class TestGenerateSummary:
    def test_perfect_score(self):
        report = ComplianceReport(
            manuscript_path="test", bible_path="test",
            score=100.0, total_checks=10, passed_checks=10,
        )
        summary = _generate_summary(report)
        assert "A+" in summary

    def test_with_errors(self):
        report = ComplianceReport(
            manuscript_path="test", bible_path="test",
            score=70.0, total_checks=10, passed_checks=7,
        )
        report.issues = [
            ValidationIssue(severity="error", category="character",
                          description="test", location="ch1"),
        ]
        summary = _generate_summary(report)
        assert "error" in summary.lower()
        assert "C" in summary

    def test_grade_levels(self):
        grades = {98: "A+", 95: "A", 91: "A-", 88: "B+",
                  85: "B", 81: "B-", 75: "C", 65: "D", 50: "F"}
        for score, expected_grade in grades.items():
            report = ComplianceReport(
                manuscript_path="t", bible_path="t", score=float(score),
            )
            summary = _generate_summary(report)
            assert expected_grade in summary, f"Score {score} should get {expected_grade}, got {summary}"


class TestValidateManuscript:
    def test_validates_clean(self, sample_manuscript_dir, sample_bible_dir, config):
        report = validate_manuscript(
            sample_manuscript_dir, sample_bible_dir, config, save_report=False,
        )
        assert report.score >= 0
        assert len(report.chapters_validated) == 2

    def test_validates_with_issues(self, sample_manuscript_with_issues, sample_bible_dir, config):
        # First ingest terminology
        conn = get_connection(config)
        TermRepository(conn).upsert(GlossaryTerm(
            term="Genesis Protocol",
            incorrect_forms=["genesis program", "protocol system"],
        ))
        TermRepository(conn).upsert(GlossaryTerm(
            term="the Order",
            incorrect_forms=["The ORDER", "the order"],
        ))
        conn.close()

        report = validate_manuscript(
            sample_manuscript_with_issues, sample_bible_dir, config, save_report=False,
        )
        # Should find placeholder text + terminology issues
        assert len(report.issues) > 0

    def test_saves_report(self, sample_manuscript_dir, sample_bible_dir, config):
        report = validate_manuscript(
            sample_manuscript_dir, sample_bible_dir, config, save_report=True,
        )
        # Check report was saved
        from series_bible_generator.db import ReportRepository
        conn = get_connection(config)
        latest = ReportRepository(conn).get_latest(str(sample_manuscript_dir))
        conn.close()
        assert latest is not None
