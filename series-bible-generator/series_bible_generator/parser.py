"""Parse existing series bible markdown files into structured data."""

import hashlib
import re
from pathlib import Path
from typing import Optional

from .config import Config, BIBLE_DOCUMENT_TYPES
from .models import (
    BibleDocument, Character, TimelineEvent, GlossaryTerm,
    Artifact, Location,
)


def find_bible_files(bible_dir: Path, prefix: str = "SERIES_BIBLE_") -> dict:
    """Find all series bible files in a directory.

    Returns dict mapping doc_type -> file_path.
    """
    found = {}
    for f in sorted(bible_dir.glob(f"{prefix}*.md")):
        name = f.stem.replace(prefix, "")
        for doc_type, pattern in BIBLE_DOCUMENT_TYPES.items():
            if pattern == name:
                found[doc_type] = f
                break
    return found


def file_checksum(path: Path) -> str:
    """Compute MD5 checksum of a file."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def parse_bible_file(file_path: Path, doc_type: str) -> BibleDocument:
    """Parse a series bible markdown file into structured data."""
    content = file_path.read_text(encoding="utf-8")
    title = _extract_title(content)
    sections = _extract_sections(content)

    doc = BibleDocument(
        doc_type=doc_type,
        title=title,
        file_path=str(file_path),
        content=content,
        sections=sections,
    )

    # Extract entities based on document type
    if doc_type == "bloodline":
        doc.characters = _parse_bloodline_characters(content, str(file_path))
    elif doc_type == "timeline":
        doc.events = _parse_timeline_events(content, str(file_path))
    elif doc_type == "terminology":
        doc.terms = _parse_terminology(content, str(file_path))
    elif doc_type == "keys":
        doc.artifacts = _parse_keys(content, str(file_path))

    return doc


def parse_all_bible_files(bible_dir: Path, config: Config) -> list:
    """Parse all bible files in a directory."""
    files = find_bible_files(bible_dir, config.bible_prefix)
    documents = []
    for doc_type, file_path in files.items():
        doc = parse_bible_file(file_path, doc_type)
        documents.append(doc)
    return documents


def _extract_title(content: str) -> str:
    """Extract the document title from markdown."""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("## "):
            return line[3:].strip()
    return ""


def _extract_sections(content: str) -> list:
    """Extract sections as (heading, content) tuples."""
    sections = []
    current_heading = ""
    current_content = []

    for line in content.split("\n"):
        if line.startswith("## ") or line.startswith("### "):
            if current_heading or current_content:
                sections.append((current_heading, "\n".join(current_content).strip()))
            current_heading = line.lstrip("#").strip().strip("*")
            current_content = []
        else:
            current_content.append(line)

    if current_heading or current_content:
        sections.append((current_heading, "\n".join(current_content).strip()))

    return sections


def _parse_bloodline_characters(content: str, source_file: str) -> list:
    """Extract characters from bloodline tracker."""
    characters = []
    # Match generation headings like "### **Generation 1: Pharaoh Tausret (Twosret)**"
    gen_pattern = re.compile(
        r"###\s+\*?\*?Generation\s+(\d+):\s*(.+?)\*?\*?\s*$",
        re.MULTILINE,
    )

    sections = content.split("###")
    for section in sections:
        match = gen_pattern.search("###" + section)
        if match:
            gen_num = int(match.group(1))
            name_raw = match.group(2).strip().strip("*")
            # Clean name — remove parenthetical
            name = re.sub(r"\s*\(.*?\)\s*", "", name_raw).strip()

            # Extract dates
            dates_match = re.search(r"\*\*Dates:\*\*\s*(.+)", section)
            era = dates_match.group(1).strip() if dates_match else ""

            # Extract role
            role_match = re.search(r"\*\*Role:\*\*\s*(.+)", section)
            description = role_match.group(1).strip() if role_match else ""

            # Aliases from parenthetical
            alias_match = re.search(r"\(([^)]+)\)", name_raw)
            aliases = [alias_match.group(1)] if alias_match else []

            char = Character(
                name=name,
                aliases=aliases,
                description=description,
                era=era,
                generation_absolute=gen_num,
                source_file=source_file,
            )
            characters.append(char)

    return characters


def _parse_timeline_events(content: str, source_file: str) -> list:
    """Extract events from master timeline."""
    events = []

    # Match chapter/event headings with dates
    event_pattern = re.compile(
        r"###\s+\*?\*?(.+?)\((\d+\s*(?:BCE|CE)(?:\s*[-–]\s*\d+\s*(?:BCE|CE))?)\)\*?\*?",
        re.MULTILINE,
    )

    for match in event_pattern.finditer(content):
        title = match.group(1).strip().strip("*:")
        date_str = match.group(2).strip()
        year = _parse_year(date_str)

        # Get description from surrounding content
        start = match.end()
        next_heading = content.find("\n###", start)
        section_text = content[start:next_heading] if next_heading > 0 else content[start:start + 500]

        # Extract characters mentioned (bold names)
        chars = re.findall(r"\*\*([A-Z][a-z]+(?:\s+[A-Za-z]+)*)\*\*", section_text)
        chars = [c for c in chars if len(c) > 2 and c not in (
            "Key", "Notes", "Location", "Historical", "Major", "Book",
            "Central", "Created", "Dates", "Role", "Status",
        )]

        # Extract location
        loc_match = re.search(r"\*\*Location:\*\*\s*(.+)", section_text)
        location = loc_match.group(1).strip() if loc_match else ""

        event = TimelineEvent(
            date=date_str,
            year_numeric=year,
            description=title,
            location=location,
            characters_involved=chars[:10],
            significance="major",
            source_file=source_file,
        )
        events.append(event)

    return events


def _parse_terminology(content: str, source_file: str) -> list:
    """Extract terms from terminology glossary."""
    terms = []

    # Split on ### headings
    sections = re.split(r"###\s+", content)

    for section in sections[1:]:  # skip preamble
        lines = section.strip().split("\n")
        if not lines:
            continue

        # Term name from heading
        term_name = lines[0].strip().strip("*").strip()
        if not term_name:
            continue

        # Extract definition
        definition = ""
        correct_usage = ""
        incorrect_forms = []
        book_notes = {}
        in_never_block = False

        for line in lines[1:]:
            line_stripped = line.strip()
            if line_stripped.startswith("**Definition:**"):
                definition = line_stripped.replace("**Definition:**", "").strip()
                in_never_block = False
            elif "Always use:" in line_stripped or "Consistent Usage:" in line_stripped:
                # Start collecting correct usage
                correct_usage = ""
                in_never_block = False
            elif "NEVER" in line_stripped and "**" in line_stripped:
                in_never_block = True
                forms = re.findall(r'"([^"]+)"', line_stripped)
                incorrect_forms.extend(forms)
            elif in_never_block and line_stripped.startswith("- "):
                forms = re.findall(r'"([^"]+)"', line_stripped)
                incorrect_forms.extend(forms)
                if not forms and not line_stripped.startswith("- **Book"):
                    # Plain list item might be an incorrect form
                    pass
            elif line_stripped.startswith("- \"") and not in_never_block:
                usage = line_stripped.lstrip("- ").strip('"').strip()
                if correct_usage:
                    correct_usage += "; " + usage
                else:
                    correct_usage = usage
            elif line_stripped.startswith("- **Book"):
                in_never_block = False
                book_match = re.match(r"- \*\*Book\s+(\d+):\*\*\s*(.*)", line_stripped)
                if book_match:
                    book_notes[f"Book {book_match.group(1)}"] = book_match.group(2).strip()
            elif line_stripped == "" or line_stripped == "---":
                in_never_block = False

        term = GlossaryTerm(
            term=term_name,
            definition=definition,
            correct_usage=correct_usage,
            incorrect_forms=incorrect_forms,
            book_specific_notes=book_notes,
            source_file=source_file,
        )
        terms.append(term)

    return terms


def _parse_keys(content: str, source_file: str) -> list:
    """Extract key artifacts from seven keys tracker."""
    artifacts = []

    # Split on key headings
    key_pattern = re.compile(
        r"###\s+\*?\*?(?:DEFENSIVE|OFFENSIVE)\s+KEY\s+(\d+):\s*[\"']?(.+?)[\"']?\*?\*?\s*$",
        re.MULTILINE,
    )

    for match in key_pattern.finditer(content):
        key_num = match.group(1)
        key_name = match.group(2).strip().strip("*\"'")
        key_type = "defensive" if "DEFENSIVE" in match.group(0) else "offensive"

        # Get section content
        start = match.end()
        next_key = key_pattern.search(content, start)
        section = content[start:next_key.start()] if next_key else content[start:start + 2000]

        # Extract description
        desc_match = re.search(r"\*\*Description:\*\*\s*(.+)", section)
        description = desc_match.group(1).strip().strip('"') if desc_match else ""

        # Extract function
        func_match = re.search(r"\*\*Function:\*\*\s*(.+)", section)
        function = func_match.group(1).strip() if func_match else ""

        artifact = Artifact(
            name=f"{key_type.title()} Key {key_num}: {key_name}",
            description=f"{description}. {function}".strip(". "),
            artifact_type="key",
            created_date="1189 BCE",
            created_by="Nefertari",
            properties={"key_number": int(key_num), "alignment": key_type},
            source_file=source_file,
        )
        artifacts.append(artifact)

    return artifacts


def _parse_year(date_str: str) -> Optional[int]:
    """Parse a date string into a numeric year (negative for BCE).

    For ranges like '1189-1100 BCE', returns the first year.
    """
    # Check for range — extract era suffix from the end
    era_match = re.search(r"(BCE|CE)\s*$", date_str.strip())
    if era_match:
        era = era_match.group(1)
        # Get the first number in the string
        num_match = re.search(r"(\d+)", date_str)
        if num_match:
            year = int(num_match.group(1))
            if era == "BCE":
                year = -year
            return year
    return None
