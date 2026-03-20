"""Tests for entity extractor."""

import pytest
from series_bible_generator.extractor import (
    _extract_without_ai, _deduplicate_characters,
    _parse_extraction_response, extract_from_manuscript,
)
from series_bible_generator.models import Character, ExtractionResult


class TestExtractWithoutAI:
    def test_extracts_character_names(self):
        text = """
        Nefertari pressed her fingers against Tausret's wrist. Nefertari stood.
        Amenhotep watched from the doorway. Amenhotep said nothing.
        Nefertari turned to face him. Amenhotep nodded.
        """
        result = _extract_without_ai(text, "chapter_01", "Book 3")
        names = [c.name for c in result.characters]
        assert "Nefertari" in names
        assert "Amenhotep" in names

    def test_ignores_common_words(self):
        text = "The Chapter Book Part This That What When Where Which"
        result = _extract_without_ai(text * 5, "ch1", "Book 1")
        names = [c.name for c in result.characters]
        assert "The" not in names
        assert "Chapter" not in names

    def test_minimum_mentions(self):
        text = "Nefertari appeared once. SingleMention appeared once."
        result = _extract_without_ai(text, "ch1", "Book 1")
        # Both appear only once, below threshold of 3
        names = [c.name for c in result.characters]
        assert "SingleMention" not in names

    def test_sets_book_info(self):
        text = "Nefertari said. Nefertari moved. Nefertari thought."
        result = _extract_without_ai(text, "chapter_01", "Book 3")
        assert result.chapters_processed == 1
        if result.characters:
            assert result.characters[0].first_appearance_book == "Book 3"


class TestDeduplicateCharacters:
    def test_merges_duplicates(self):
        chars = [
            Character(name="Nefertari", description="Short"),
            Character(name="Nefertari", description="Longer description here"),
        ]
        result = _deduplicate_characters(chars)
        assert len(result) == 1
        assert result[0].description == "Longer description here"

    def test_merges_aliases(self):
        chars = [
            Character(name="Jesus", aliases=["Yeshua"]),
            Character(name="Jesus", aliases=["Jesus of Nazareth"]),
        ]
        result = _deduplicate_characters(chars)
        assert len(result) == 1
        assert "Yeshua" in result[0].aliases
        assert "Jesus of Nazareth" in result[0].aliases

    def test_merges_traits(self):
        chars = [
            Character(name="Sarah", traits=["intelligent"]),
            Character(name="Sarah", traits=["determined"]),
        ]
        result = _deduplicate_characters(chars)
        assert set(result[0].traits) == {"intelligent", "determined"}

    def test_no_duplicates(self):
        chars = [
            Character(name="A"),
            Character(name="B"),
        ]
        result = _deduplicate_characters(chars)
        assert len(result) == 2


class TestParseExtractionResponse:
    def test_valid_json(self):
        response = """{
            "characters": [
                {"name": "Nefertari", "role": "protagonist", "description": "Physician"}
            ],
            "events": [
                {"date": "1189 BCE", "description": "Collapse", "significance": "major"}
            ],
            "locations": [
                {"name": "Pi-Ramesses", "description": "Capital city"}
            ],
            "terms": [
                {"term": "Genesis Protocol", "definition": "Memory system"}
            ],
            "artifacts": [
                {"name": "Key 1", "artifact_type": "key"}
            ]
        }"""
        result = _parse_extraction_response(response, "ch1", "Book 3")
        assert len(result.characters) == 1
        assert result.characters[0].name == "Nefertari"
        assert len(result.events) == 1
        assert len(result.locations) == 1
        assert len(result.terms) == 1
        assert len(result.artifacts) == 1

    def test_json_in_markdown(self):
        response = """Here are the extracted entities:
```json
{
    "characters": [{"name": "Test"}],
    "events": [],
    "locations": [],
    "terms": [],
    "artifacts": []
}
```
"""
        result = _parse_extraction_response(response, "ch1", "Book 1")
        assert len(result.characters) == 1

    def test_invalid_json(self):
        result = _parse_extraction_response("not json", "ch1", "Book 1")
        assert result.total_entities == 0

    def test_empty_response(self):
        result = _parse_extraction_response("", "ch1", "Book 1")
        assert result.total_entities == 0


class TestExtractFromManuscript:
    def test_extracts_from_dir(self, sample_manuscript_dir, config):
        result = extract_from_manuscript(sample_manuscript_dir, "Book 3", config)
        assert result.chapters_processed == 2
        names = [c.name for c in result.characters]
        # Without AI, regex extraction needs 3+ mentions per chapter
        # Amenhotep appears 3+ times across the sample chapters
        assert len(names) >= 1

    def test_single_file(self, sample_manuscript_dir, config):
        single = sample_manuscript_dir / "chapter_01.md"
        result = extract_from_manuscript(single, "Book 3", config)
        assert result.chapters_processed == 1
