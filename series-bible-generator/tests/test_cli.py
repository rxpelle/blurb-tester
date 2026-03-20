"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from series_bible_generator.cli import main
from series_bible_generator.db import get_connection, TermRepository
from series_bible_generator.models import GlossaryTerm


@pytest.fixture
def runner():
    return CliRunner()


class TestMainGroup:
    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Series Bible Generator" in result.output

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestIngestCommand:
    def test_ingest(self, runner, sample_bible_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        result = runner.invoke(main, ["ingest", "-b", str(sample_bible_dir)])
        assert result.exit_code == 0
        assert "Ingested" in result.output

    def test_ingest_no_files(self, runner, tmp_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        empty = tmp_dir / "empty"
        empty.mkdir()
        result = runner.invoke(main, ["ingest", "-b", str(empty)])
        assert "No bible files" in result.output

    def test_ingest_skip_unchanged(self, runner, sample_bible_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        # First ingest
        runner.invoke(main, ["ingest", "-b", str(sample_bible_dir)])
        # Second ingest — should skip
        result = runner.invoke(main, ["ingest", "-b", str(sample_bible_dir)])
        assert "Skipping" in result.output or "unchanged" in result.output

    def test_ingest_force(self, runner, sample_bible_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        runner.invoke(main, ["ingest", "-b", str(sample_bible_dir)])
        result = runner.invoke(main, ["ingest", "-b", str(sample_bible_dir), "--force"])
        assert "Ingested" in result.output


class TestExtractCommand:
    def test_extract(self, runner, sample_manuscript_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        result = runner.invoke(main, [
            "extract", "-m", str(sample_manuscript_dir), "-b", "Book 3",
        ])
        assert result.exit_code == 0

    def test_extract_to_file(self, runner, sample_manuscript_dir, tmp_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        out = tmp_dir / "output.txt"
        result = runner.invoke(main, [
            "extract", "-m", str(sample_manuscript_dir), "-b", "Book 3",
            "-o", str(out),
        ])
        assert result.exit_code == 0
        assert out.exists()


class TestQueryCommand:
    def test_query_empty_db(self, runner, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        get_connection(config).close()  # ensure db exists
        result = runner.invoke(main, ["query", "Nefertari"])
        assert result.exit_code == 0

    def test_query_with_bible_dir(self, runner, sample_bible_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        result = runner.invoke(main, [
            "query", "Nefertari", "-b", str(sample_bible_dir),
        ])
        assert result.exit_code == 0


class TestValidateCommand:
    def test_validate(self, runner, sample_manuscript_dir, sample_bible_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        result = runner.invoke(main, [
            "validate", "-m", str(sample_manuscript_dir),
            "-b", str(sample_bible_dir),
        ])
        assert result.exit_code == 0

    def test_validate_to_file(self, runner, sample_manuscript_dir, sample_bible_dir,
                              tmp_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        out = tmp_dir / "report.md"
        result = runner.invoke(main, [
            "validate", "-m", str(sample_manuscript_dir),
            "-b", str(sample_bible_dir), "-o", str(out),
        ])
        assert result.exit_code == 0
        assert out.exists()
        assert "COMPLIANCE REPORT" in out.read_text()


class TestStatusCommand:
    def test_status_empty(self, runner, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0

    def test_status_after_ingest(self, runner, sample_bible_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        runner.invoke(main, ["ingest", "-b", str(sample_bible_dir)])
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0


class TestListCommand:
    def test_list_characters(self, runner, sample_bible_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        runner.invoke(main, ["ingest", "-b", str(sample_bible_dir)])
        result = runner.invoke(main, ["list-entities", "-e", "characters"])
        assert result.exit_code == 0

    def test_list_terms(self, runner, sample_bible_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        runner.invoke(main, ["ingest", "-b", str(sample_bible_dir)])
        result = runner.invoke(main, ["list-entities", "-e", "terms"])
        assert result.exit_code == 0

    def test_list_artifacts(self, runner, sample_bible_dir, config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        runner.invoke(main, ["ingest", "-b", str(sample_bible_dir)])
        result = runner.invoke(main, ["list-entities", "-e", "artifacts"])
        assert result.exit_code == 0


class TestHistoryCommand:
    def test_no_history(self, runner, config, monkeypatch, tmp_dir):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        get_connection(config).close()
        # Create a real path so click doesn't reject it
        dummy = tmp_dir / "dummy_manuscript"
        dummy.mkdir()
        result = runner.invoke(main, ["history", "-m", str(dummy)])
        assert result.exit_code == 0
        assert "No validation history" in result.output

    def test_with_history(self, runner, sample_manuscript_dir, sample_bible_dir,
                          config, monkeypatch):
        monkeypatch.setenv("SERIES_BIBLE_DATA_DIR", str(config.data_dir))
        runner.invoke(main, [
            "validate", "-m", str(sample_manuscript_dir),
            "-b", str(sample_bible_dir),
        ])
        result = runner.invoke(main, ["history", "-m", str(sample_manuscript_dir)])
        assert result.exit_code == 0
