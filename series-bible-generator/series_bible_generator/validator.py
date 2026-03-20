"""Validate manuscripts against the series bible."""

import re
from pathlib import Path
from typing import Optional

from anthropic import Anthropic

from .config import Config
from .db import (
    get_connection, CharacterRepository, EventRepository,
    TermRepository, ArtifactRepository, ReportRepository,
)
from .models import ComplianceReport, ValidationIssue


VALIDATE_PROMPT = """You are a series bible compliance validator. Check the manuscript chapter against the series bible data and report any inconsistencies.

For each check, report:
- severity: "error" (factual contradiction), "warning" (potential issue), or "info" (minor style note)
- category: "character", "timeline", "terminology", "artifact", or "continuity"
- description: What the issue is
- location: Where in the manuscript (chapter/paragraph reference)
- bible_reference: Which bible document/section is contradicted
- suggestion: How to fix it

Return valid JSON array of issues:
[
  {{"severity": "...", "category": "...", "description": "...", "location": "...", "bible_reference": "...", "suggestion": "..."}}
]

If no issues found, return an empty array: []

SERIES BIBLE DATA:
{bible_data}

MANUSCRIPT CHAPTER ({chapter_name}):
{chapter_text}
"""


def validate_manuscript(
    manuscript_path: Path,
    bible_path: Path,
    config: Config,
    save_report: bool = True,
) -> ComplianceReport:
    """Validate a manuscript against the series bible."""
    report = ComplianceReport(
        manuscript_path=str(manuscript_path),
        bible_path=str(bible_path),
    )

    # Load bible content
    bible_content = _load_bible_content(bible_path, config)

    # Load manuscript chapters
    chapter_files = sorted(manuscript_path.glob("*.md")) if manuscript_path.is_dir() else [manuscript_path]

    for chapter_file in chapter_files:
        chapter_text = chapter_file.read_text(encoding="utf-8")
        chapter_name = chapter_file.stem

        # Run structural checks (no AI needed)
        structural_issues = _check_structural(chapter_text, chapter_name, config)
        for issue in structural_issues:
            report.add_issue(issue)

        # Run terminology checks
        term_issues = _check_terminology(chapter_text, chapter_name, config)
        for issue in term_issues:
            report.add_issue(issue)
        # Count passes for clean terminology
        report.add_pass()

        # Run AI-powered deep validation if available
        if config.has_api_key and bible_content:
            ai_issues = _validate_with_ai(
                chapter_text, chapter_name, bible_content, config,
            )
            for issue in ai_issues:
                report.add_issue(issue)
            report.add_pass()  # AI check completed

        report.chapters_validated.append(chapter_name)

    report.calculate_score()
    report.summary = _generate_summary(report)

    # Save to database
    if save_report:
        conn = get_connection(config)
        ReportRepository(conn).save(report)
        conn.close()

    return report


def validate_chapter(
    chapter_text: str,
    chapter_name: str,
    bible_path: Path,
    config: Config,
) -> list:
    """Validate a single chapter, returning list of ValidationIssues."""
    issues = []

    bible_content = _load_bible_content(bible_path, config)
    issues.extend(_check_structural(chapter_text, chapter_name, config))
    issues.extend(_check_terminology(chapter_text, chapter_name, config))

    if config.has_api_key and bible_content:
        issues.extend(_validate_with_ai(chapter_text, chapter_name, bible_content, config))

    return issues


def _load_bible_content(bible_path: Path, config: Config) -> str:
    """Load and concatenate bible files for validation context."""
    if bible_path.is_file():
        return bible_path.read_text(encoding="utf-8")

    from .parser import find_bible_files
    files = find_bible_files(bible_path, config.bible_prefix)
    parts = []
    for doc_type, file_path in files.items():
        content = file_path.read_text(encoding="utf-8")
        # Truncate each file to keep within context limits
        parts.append(f"--- {doc_type.upper()} ---\n{content[:8000]}")

    return "\n\n".join(parts)


def _check_structural(
    text: str,
    chapter_name: str,
    config: Config,
) -> list:
    """Check structural issues (no AI needed)."""
    issues = []

    # Check for common formatting issues
    if text.count("# ") == 0:
        issues.append(ValidationIssue(
            severity="info",
            category="continuity",
            description="No markdown headings found in chapter",
            location=chapter_name,
        ))

    # Check for very short chapters (potential truncation)
    word_count = len(text.split())
    if word_count < 500:
        issues.append(ValidationIssue(
            severity="warning",
            category="continuity",
            description=f"Very short chapter ({word_count} words) — possible truncation",
            location=chapter_name,
        ))

    # Check for placeholder text
    placeholders = ["TODO", "FIXME", "TBD", "[INSERT", "XXX", "PLACEHOLDER"]
    for placeholder in placeholders:
        if placeholder in text:
            issues.append(ValidationIssue(
                severity="warning",
                category="continuity",
                description=f"Placeholder text found: {placeholder}",
                location=chapter_name,
            ))

    return issues


def _check_terminology(
    text: str,
    chapter_name: str,
    config: Config,
) -> list:
    """Check terminology consistency against database."""
    issues = []

    conn = get_connection(config)
    terms = TermRepository(conn).get_all()
    conn.close()

    for term_row in terms:
        incorrect_forms = []
        try:
            import json
            incorrect_forms = json.loads(term_row.get("incorrect_forms", "[]"))
        except (json.JSONDecodeError, TypeError):
            pass

        for wrong_form in incorrect_forms:
            if wrong_form and wrong_form in text:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="terminology",
                    description=f"Incorrect term form '{wrong_form}' — should be '{term_row['term']}'",
                    location=chapter_name,
                    bible_reference=f"Terminology Glossary: {term_row['term']}",
                    suggestion=f"Use '{term_row.get('correct_usage', term_row['term'])}' instead",
                ))

    return issues


def _validate_with_ai(
    chapter_text: str,
    chapter_name: str,
    bible_content: str,
    config: Config,
) -> list:
    """Use Claude for deep semantic validation."""
    client = Anthropic(api_key=config.anthropic_api_key)

    response = client.messages.create(
        model=config.model,
        max_tokens=config.max_tokens,
        messages=[{
            "role": "user",
            "content": VALIDATE_PROMPT.format(
                bible_data=bible_content[:25000],
                chapter_name=chapter_name,
                chapter_text=chapter_text[:25000],
            ),
        }],
    )

    return _parse_validation_response(response.content[0].text)


def _parse_validation_response(response_text: str) -> list:
    """Parse AI validation response into ValidationIssues."""
    import json

    issues = []
    json_match = re.search(r"\[[\s\S]*\]", response_text)
    if not json_match:
        return issues

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        return issues

    for item in data:
        try:
            issue = ValidationIssue(
                severity=item.get("severity", "info"),
                category=item.get("category", "continuity"),
                description=item.get("description", ""),
                location=item.get("location", ""),
                bible_reference=item.get("bible_reference", ""),
                suggestion=item.get("suggestion", ""),
            )
            issues.append(issue)
        except ValueError:
            continue

    return issues


def _generate_summary(report: ComplianceReport) -> str:
    """Generate a human-readable summary."""
    grade = "A+" if report.score >= 98 else \
            "A" if report.score >= 93 else \
            "A-" if report.score >= 90 else \
            "B+" if report.score >= 87 else \
            "B" if report.score >= 83 else \
            "B-" if report.score >= 80 else \
            "C" if report.score >= 70 else \
            "D" if report.score >= 60 else "F"

    parts = [f"Grade: {grade} ({report.score}/100)"]

    if report.errors:
        parts.append(f"{len(report.errors)} error(s) require immediate attention.")

    categories = {}
    for issue in report.issues:
        categories[issue.category] = categories.get(issue.category, 0) + 1
    if categories:
        cats = ", ".join(f"{k}: {v}" for k, v in sorted(categories.items()))
        parts.append(f"Issues by category: {cats}")

    return " ".join(parts)
