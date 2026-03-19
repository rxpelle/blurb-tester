"""Tests for CLI commands."""

import json
import os
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner
from geo_optimizer.cli import main

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def runner():
    return CliRunner()


class TestAnalyzeCommand:
    def test_analyze_markdown_file(self, runner):
        filepath = os.path.join(FIXTURES_DIR, 'good_blog_post.md')
        result = runner.invoke(main, ['analyze', filepath])
        assert result.exit_code == 0
        assert 'GEO Score' in result.output

    def test_analyze_html_file(self, runner):
        filepath = os.path.join(FIXTURES_DIR, 'page_with_schema.html')
        result = runner.invoke(main, ['analyze', filepath])
        assert result.exit_code == 0

    def test_analyze_missing_file(self, runner):
        result = runner.invoke(main, ['analyze', '/nonexistent/file.md'])
        assert result.exit_code != 0

    def test_analyze_json_output(self, runner):
        filepath = os.path.join(FIXTURES_DIR, 'good_blog_post.md')
        result = runner.invoke(main, ['-o', 'json', 'analyze', filepath])
        assert result.exit_code == 0
        # Should be valid JSON
        data = json.loads(result.output)
        assert 'score' in data
        assert 'results' in data
        assert 'recommendations' in data

    def test_analyze_url(self, runner):
        mock_response = MagicMock()
        mock_response.text = '<html><body><h1>Test</h1><p>Content here.</p></body></html>'
        mock_response.raise_for_status = MagicMock()

        with patch('geo_optimizer.cli.requests.get', return_value=mock_response):
            result = runner.invoke(main, ['analyze', '--url', 'https://example.com'])
            assert result.exit_code == 0


class TestScoreCommand:
    def test_score_file(self, runner):
        filepath = os.path.join(FIXTURES_DIR, 'good_blog_post.md')
        result = runner.invoke(main, ['score', filepath])
        assert result.exit_code == 0
        assert 'GEO Score' in result.output

    def test_score_json_output(self, runner):
        filepath = os.path.join(FIXTURES_DIR, 'poor_blog_post.md')
        result = runner.invoke(main, ['-o', 'json', 'score', filepath])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'overall_score' in data

    def test_score_url(self, runner):
        mock_response = MagicMock()
        mock_response.text = '<html><body><p>Simple page</p></body></html>'
        mock_response.raise_for_status = MagicMock()

        with patch('geo_optimizer.cli.requests.get', return_value=mock_response):
            result = runner.invoke(main, ['score', '--url', 'https://example.com'])
            assert result.exit_code == 0


class TestCompareCommand:
    def test_compare_two_files(self, runner):
        file1 = os.path.join(FIXTURES_DIR, 'good_blog_post.md')
        file2 = os.path.join(FIXTURES_DIR, 'poor_blog_post.md')
        result = runner.invoke(main, ['compare', file1, file2])
        assert result.exit_code == 0
        assert 'Comparison' in result.output

    def test_compare_json_output(self, runner):
        file1 = os.path.join(FIXTURES_DIR, 'good_blog_post.md')
        file2 = os.path.join(FIXTURES_DIR, 'poor_blog_post.md')
        result = runner.invoke(main, ['-o', 'json', 'compare', file1, file2])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert file1 in data or 'good_blog_post' in str(data)

    def test_compare_missing_file(self, runner):
        file1 = os.path.join(FIXTURES_DIR, 'good_blog_post.md')
        result = runner.invoke(main, ['compare', file1, '/nonexistent.md'])
        assert result.exit_code != 0


class TestVersion:
    def test_version_flag(self, runner):
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert '0.1.0' in result.output


class TestNoInput:
    def test_analyze_no_file_no_url(self, runner):
        result = runner.invoke(main, ['analyze'])
        assert result.exit_code != 0

    def test_score_no_file_no_url(self, runner):
        result = runner.invoke(main, ['score'])
        assert result.exit_code != 0
