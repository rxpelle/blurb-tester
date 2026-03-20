"""Extract entities from manuscript chapters using Claude."""

import json
import re
from pathlib import Path

from anthropic import Anthropic

from .config import Config
from .models import (
    Character, TimelineEvent, GlossaryTerm, Location,
    Artifact, ExtractionResult,
)


EXTRACTION_PROMPT = """You are a series bible extraction engine. Analyze the manuscript chapter below and extract all entities into structured JSON.

Extract:
1. **Characters**: name, aliases, description, role (protagonist/antagonist/supporting/mentioned), network affiliation (defensive/offensive/neutral/unknown), traits, relationships to other characters, locations
2. **Timeline Events**: date/year, description, characters involved, location, significance (major/minor/background)
3. **Locations**: name, aliases, description, era
4. **Terms/Concepts**: specialized terminology, definitions, usage rules
5. **Artifacts**: significant objects, their descriptions, holders

For each entity, include ONLY what's explicitly stated or strongly implied in the text. Do NOT infer or fabricate details.

Return valid JSON with this structure:
{
  "characters": [
    {"name": "...", "aliases": [], "description": "...", "role": "...", "network": "...", "traits": [], "relationships": ["relationship_description"], "locations": []}
  ],
  "events": [
    {"date": "...", "year_numeric": null, "description": "...", "characters_involved": [], "location": "...", "significance": "..."}
  ],
  "locations": [
    {"name": "...", "aliases": [], "description": "...", "era": "..."}
  ],
  "terms": [
    {"term": "...", "definition": "...", "correct_usage": "..."}
  ],
  "artifacts": [
    {"name": "...", "description": "...", "artifact_type": "...", "created_by": "...", "current_holder": "..."}
  ]
}

MANUSCRIPT CHAPTER:
"""


def extract_from_chapter(
    chapter_text: str,
    chapter_name: str,
    book_name: str,
    config: Config,
) -> ExtractionResult:
    """Extract entities from a single chapter using Claude."""
    if not config.has_api_key:
        return _extract_without_ai(chapter_text, chapter_name, book_name)

    client = Anthropic(api_key=config.anthropic_api_key)
    response = client.messages.create(
        model=config.model,
        max_tokens=config.max_tokens,
        messages=[{
            "role": "user",
            "content": EXTRACTION_PROMPT + chapter_text[:50000],
        }],
    )

    result_text = response.content[0].text
    return _parse_extraction_response(result_text, chapter_name, book_name)


def extract_from_manuscript(
    manuscript_path: Path,
    book_name: str,
    config: Config,
) -> ExtractionResult:
    """Extract entities from all chapters in a manuscript directory."""
    chapter_files = sorted(manuscript_path.glob("*.md"))
    if not chapter_files:
        # Try single file
        if manuscript_path.is_file():
            chapter_files = [manuscript_path]

    combined = ExtractionResult(manuscript_path=str(manuscript_path))

    for chapter_file in chapter_files:
        text = chapter_file.read_text(encoding="utf-8")
        chapter_result = extract_from_chapter(
            text, chapter_file.stem, book_name, config,
        )
        # Merge results
        combined.characters.extend(chapter_result.characters)
        combined.events.extend(chapter_result.events)
        combined.terms.extend(chapter_result.terms)
        combined.locations.extend(chapter_result.locations)
        combined.artifacts.extend(chapter_result.artifacts)
        combined.chapters_processed += 1

    # Deduplicate characters by name
    combined.characters = _deduplicate_characters(combined.characters)
    return combined


def _parse_extraction_response(
    response_text: str,
    chapter_name: str,
    book_name: str,
) -> ExtractionResult:
    """Parse Claude's JSON response into an ExtractionResult."""
    result = ExtractionResult(manuscript_path=chapter_name, chapters_processed=1)

    # Extract JSON from response
    json_match = re.search(r"\{[\s\S]*\}", response_text)
    if not json_match:
        return result

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        return result

    # Parse characters
    for c in data.get("characters", []):
        char = Character(
            name=c.get("name", ""),
            aliases=c.get("aliases", []),
            description=c.get("description", ""),
            first_appearance_book=book_name,
            first_appearance_chapter=chapter_name,
            role=c.get("role", ""),
            network=c.get("network", "unknown"),
            traits=c.get("traits", []),
            relationships=c.get("relationships", []),
            locations=c.get("locations", []),
            source_file=chapter_name,
        )
        result.characters.append(char)

    # Parse events
    for e in data.get("events", []):
        event = TimelineEvent(
            date=e.get("date", ""),
            year_numeric=e.get("year_numeric"),
            description=e.get("description", ""),
            book=book_name,
            chapter=chapter_name,
            characters_involved=e.get("characters_involved", []),
            location=e.get("location", ""),
            significance=e.get("significance", "minor"),
            source_file=chapter_name,
        )
        result.events.append(event)

    # Parse locations
    for loc in data.get("locations", []):
        location = Location(
            name=loc.get("name", ""),
            aliases=loc.get("aliases", []),
            description=loc.get("description", ""),
            era=loc.get("era", ""),
            books_featured=[book_name],
            source_file=chapter_name,
        )
        result.locations.append(location)

    # Parse terms
    for t in data.get("terms", []):
        term = GlossaryTerm(
            term=t.get("term", ""),
            definition=t.get("definition", ""),
            correct_usage=t.get("correct_usage", ""),
            source_file=chapter_name,
        )
        result.terms.append(term)

    # Parse artifacts
    for a in data.get("artifacts", []):
        artifact = Artifact(
            name=a.get("name", ""),
            description=a.get("description", ""),
            artifact_type=a.get("artifact_type", ""),
            created_by=a.get("created_by", ""),
            current_holder=a.get("current_holder", ""),
            source_file=chapter_name,
        )
        result.artifacts.append(artifact)

    return result


def _extract_without_ai(
    text: str,
    chapter_name: str,
    book_name: str,
) -> ExtractionResult:
    """Basic entity extraction without AI (regex-based fallback)."""
    result = ExtractionResult(manuscript_path=chapter_name, chapters_processed=1)

    # Extract character names (capitalized words appearing multiple times)
    name_pattern = re.compile(r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)*)\b")
    name_counts = {}
    for match in name_pattern.finditer(text):
        name = match.group(1)
        name_counts[name] = name_counts.get(name, 0) + 1

    common_words = {
        "The", "Chapter", "Book", "Part", "This", "That", "What",
        "When", "Where", "Which", "Who", "How", "Why", "And",
        "But", "For", "Not", "His", "Her", "Then", "There",
    }

    for name, count in name_counts.items():
        if count >= 3 and name not in common_words:
            char = Character(
                name=name,
                first_appearance_book=book_name,
                first_appearance_chapter=chapter_name,
                source_file=chapter_name,
            )
            result.characters.append(char)

    return result


def _deduplicate_characters(characters: list) -> list:
    """Merge duplicate characters by name."""
    seen = {}
    for char in characters:
        if char.name in seen:
            existing = seen[char.name]
            # Merge aliases
            for alias in char.aliases:
                if alias not in existing.aliases:
                    existing.aliases.append(alias)
            # Keep longer description
            if len(char.description) > len(existing.description):
                existing.description = char.description
            # Merge traits
            for trait in char.traits:
                if trait not in existing.traits:
                    existing.traits.append(trait)
            # Merge relationships
            for rel in char.relationships:
                if rel not in existing.relationships:
                    existing.relationships.append(rel)
        else:
            seen[char.name] = char
    return list(seen.values())
