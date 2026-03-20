"""Generate and update series bible entries using Claude."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from anthropic import Anthropic

from .config import Config
from .models import BibleDocument, ExtractionResult


GENERATE_PROMPT = """You are a series bible author. Generate a comprehensive series bible entry in markdown format.

The entry should follow this structure for the given document type:

**For "character_index":**
Create a character reference organized by book/era with:
- Full name, aliases, generation numbers (both LOCAL and ABSOLUTE if applicable)
- Role, network affiliation (defensive/offensive)
- Key relationships
- Status (alive/dead at end of their arc)

**For "timeline":**
Create chronological entries with:
- Date and location
- Key events and their significance
- Characters involved
- Cross-references to other books

**For "terminology":**
Create glossary entries with:
- Term and definition
- Correct usage (capitalization, context)
- Incorrect forms to avoid
- Book-specific usage notes

**For "artifact_tracker":**
Create movement logs with:
- Artifact name and description
- Creation date and creator
- Complete custody chain with dates
- Current status/location

Use markdown formatting. Be precise and factual — include ONLY information supported by the provided data.

DOCUMENT TYPE: {doc_type}
BOOK/SERIES: {book_name}

EXTRACTED DATA:
{data}

EXISTING BIBLE CONTENT (if any, for context):
{existing}
"""

UPDATE_PROMPT = """You are a series bible editor. Update the existing series bible document with new information extracted from a manuscript.

Rules:
1. PRESERVE all existing entries — do not remove anything
2. ADD new entries where they belong chronologically/alphabetically
3. UPDATE existing entries only if the new data adds detail or corrects an error
4. Mark any conflicts with [CONFLICT: ...] tags for human review
5. Maintain the existing markdown formatting style exactly

EXISTING DOCUMENT:
{existing}

NEW DATA TO INTEGRATE:
{new_data}

BOOK SOURCE: {book_name}

Return the complete updated document in markdown.
"""


def generate_bible_entry(
    doc_type: str,
    extraction: ExtractionResult,
    config: Config,
    book_name: str = "",
    existing_content: str = "",
) -> str:
    """Generate a new series bible entry from extracted data."""
    if not config.has_api_key:
        return _generate_without_ai(doc_type, extraction)

    data = _format_extraction_data(extraction)

    client = Anthropic(api_key=config.anthropic_api_key)
    response = client.messages.create(
        model=config.model,
        max_tokens=config.max_tokens,
        messages=[{
            "role": "user",
            "content": GENERATE_PROMPT.format(
                doc_type=doc_type,
                book_name=book_name or "Unknown",
                data=data,
                existing=existing_content[:10000] if existing_content else "(none)",
            ),
        }],
    )

    return response.content[0].text


def update_bible_document(
    existing_content: str,
    extraction: ExtractionResult,
    config: Config,
    book_name: str = "",
) -> str:
    """Update an existing bible document with new extracted data."""
    if not config.has_api_key:
        return existing_content + "\n\n" + _generate_without_ai("update", extraction)

    new_data = _format_extraction_data(extraction)

    client = Anthropic(api_key=config.anthropic_api_key)
    response = client.messages.create(
        model=config.model,
        max_tokens=config.max_tokens,
        messages=[{
            "role": "user",
            "content": UPDATE_PROMPT.format(
                existing=existing_content,
                new_data=new_data,
                book_name=book_name or "Unknown",
            ),
        }],
    )

    return response.content[0].text


def generate_compliance_markdown(report) -> str:
    """Generate a compliance report in markdown format."""
    lines = [
        f"# SERIES BIBLE COMPLIANCE REPORT",
        f"",
        f"**Manuscript:** {report.manuscript_path}",
        f"**Bible:** {report.bible_path}",
        f"**Date:** {report.report_date}",
        f"**Score:** {report.score}/100",
        f"",
        f"---",
        f"",
        f"## Summary",
        f"",
        f"- Total checks: {report.total_checks}",
        f"- Passed: {report.passed_checks}",
        f"- Issues: {len(report.issues)}",
        f"  - Errors: {len(report.errors)}",
        f"  - Warnings: {len(report.warnings)}",
        f"  - Info: {len(report.info_items)}",
        f"",
    ]

    if report.summary:
        lines.extend([report.summary, ""])

    if report.errors:
        lines.extend(["## Errors", ""])
        for issue in report.errors:
            lines.append(f"- **{issue.category}** ({issue.location}): {issue.description}")
            if issue.bible_reference:
                lines.append(f"  - Bible ref: {issue.bible_reference}")
            if issue.suggestion:
                lines.append(f"  - Suggestion: {issue.suggestion}")
        lines.append("")

    if report.warnings:
        lines.extend(["## Warnings", ""])
        for issue in report.warnings:
            lines.append(f"- **{issue.category}** ({issue.location}): {issue.description}")
            if issue.suggestion:
                lines.append(f"  - Suggestion: {issue.suggestion}")
        lines.append("")

    if report.info_items:
        lines.extend(["## Info", ""])
        for issue in report.info_items:
            lines.append(f"- **{issue.category}** ({issue.location}): {issue.description}")
        lines.append("")

    if report.chapters_validated:
        lines.extend(["## Chapters Validated", ""])
        for ch in report.chapters_validated:
            lines.append(f"- {ch}")
        lines.append("")

    return "\n".join(lines)


def _format_extraction_data(extraction: ExtractionResult) -> str:
    """Format extraction data as readable text for the prompt."""
    parts = []

    if extraction.characters:
        parts.append("CHARACTERS:")
        for c in extraction.characters:
            parts.append(f"  - {c.name} ({c.role or 'unknown role'}): {c.description}")
            if c.aliases:
                parts.append(f"    Aliases: {', '.join(c.aliases)}")
            if c.relationships:
                parts.append(f"    Relationships: {'; '.join(c.relationships)}")

    if extraction.events:
        parts.append("\nTIMELINE EVENTS:")
        for e in extraction.events:
            parts.append(f"  - {e.date}: {e.description}")
            if e.characters_involved:
                parts.append(f"    Characters: {', '.join(e.characters_involved)}")

    if extraction.terms:
        parts.append("\nTERMINOLOGY:")
        for t in extraction.terms:
            parts.append(f"  - {t.term}: {t.definition}")

    if extraction.locations:
        parts.append("\nLOCATIONS:")
        for loc in extraction.locations:
            parts.append(f"  - {loc.name}: {loc.description}")

    if extraction.artifacts:
        parts.append("\nARTIFACTS:")
        for a in extraction.artifacts:
            parts.append(f"  - {a.name}: {a.description}")

    return "\n".join(parts) if parts else "(no data extracted)"


def _generate_without_ai(doc_type: str, extraction: ExtractionResult) -> str:
    """Generate basic bible entry without AI."""
    lines = [
        f"# Series Bible Entry — {doc_type.replace('_', ' ').title()}",
        f"",
        f"*Generated {datetime.now().strftime('%Y-%m-%d')}*",
        f"",
    ]

    if extraction.characters:
        lines.extend(["## Characters", ""])
        for c in extraction.characters:
            lines.append(f"### {c.name}")
            if c.aliases:
                lines.append(f"**Aliases:** {', '.join(c.aliases)}")
            if c.description:
                lines.append(f"**Description:** {c.description}")
            if c.role:
                lines.append(f"**Role:** {c.role}")
            if c.network:
                lines.append(f"**Network:** {c.network}")
            lines.append("")

    if extraction.events:
        lines.extend(["## Timeline", ""])
        for e in sorted(extraction.events, key=lambda x: x.year_numeric or 0):
            lines.append(f"- **{e.date}:** {e.description}")
        lines.append("")

    if extraction.terms:
        lines.extend(["## Terminology", ""])
        for t in extraction.terms:
            lines.append(f"### {t.term}")
            lines.append(f"{t.definition}")
            lines.append("")

    return "\n".join(lines)
