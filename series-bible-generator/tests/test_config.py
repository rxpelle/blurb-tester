"""Tests for configuration."""

import os
from pathlib import Path

import pytest
from series_bible_generator.config import Config, BIBLE_DOCUMENT_TYPES, DEFAULT_DATA_DIR


class TestConfig:
    def test_default_values(self):
        c = Config()
        assert c.model == "claude-sonnet-4-20250514"
        assert c.max_tokens == 4096
        assert c.bible_prefix == "SERIES_BIBLE_"

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
        c = Config.from_env()
        assert c.anthropic_api_key == "test-key-123"
        assert c.has_api_key is True

    def test_no_api_key(self):
        c = Config()
        assert c.has_api_key is False

    def test_db_path(self, tmp_dir):
        c = Config(data_dir=tmp_dir)
        assert c.db_path == tmp_dir / "series_bible.db"

    def test_custom_model(self, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_MODEL", "claude-opus-4-20250514")
        c = Config.from_env()
        assert c.model == "claude-opus-4-20250514"

    def test_default_data_dir(self):
        c = Config()
        assert c.data_dir == DEFAULT_DATA_DIR


class TestBibleDocumentTypes:
    def test_all_types_present(self):
        expected = {"timeline", "bloodline", "keys", "terminology",
                   "network", "continuity", "collapse", "dynamics"}
        assert set(BIBLE_DOCUMENT_TYPES.keys()) == expected

    def test_patterns_unique(self):
        values = list(BIBLE_DOCUMENT_TYPES.values())
        assert len(values) == len(set(values))
