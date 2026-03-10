"""Tests for the CLI interface."""

import os
import pytest
import yaml

from click.testing import CliRunner

from book_formatter.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLIVersion:
    """Tests for the version command."""

    def test_version_flag(self, runner):
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert 'book-formatter' in result.output

    def test_version_command(self, runner):
        result = runner.invoke(main, ['version'])
        assert result.exit_code == 0
        assert 'book-formatter' in result.output


class TestCLIInit:
    """Tests for the init command."""

    def test_creates_config_file(self, runner, tmp_dir):
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            result = runner.invoke(main, ['init'], input='My Book\nJane Doe\n')
            assert result.exit_code == 0
            assert os.path.exists('book.yaml')

    def test_config_contains_title(self, runner, tmp_dir):
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            result = runner.invoke(main, ['init'], input='My Book\nJane Doe\n')
            with open('book.yaml') as f:
                content = f.read()
            assert 'My Book' in content
            assert 'Jane Doe' in content

    def test_init_with_options(self, runner, tmp_dir):
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            result = runner.invoke(main, [
                'init', '--title', 'Test Book', '--author', 'Author',
                '--style', 'thriller'
            ])
            assert result.exit_code == 0
            with open('book.yaml') as f:
                content = f.read()
            assert 'thriller' in content

    def test_init_no_overwrite_without_confirm(self, runner, tmp_dir):
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            # Create existing config
            with open('book.yaml', 'w') as f:
                f.write('title: existing')

            result = runner.invoke(main, ['init', '--title', 'New', '--author', 'A'],
                                   input='n\n')
            assert result.exit_code == 0
            with open('book.yaml') as f:
                content = f.read()
            assert 'existing' in content


class TestCLIValidate:
    """Tests for the validate command."""

    def test_validate_missing_config(self, runner, tmp_dir):
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            result = runner.invoke(main, ['validate'])
            assert result.exit_code != 0
            assert 'Error' in result.output

    def test_validate_with_chapters(self, runner, tmp_dir):
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            # Create config and chapters
            os.makedirs('chapters')
            for i in range(3):
                with open(f'chapters/{i+1:02d}_CHAPTER.md', 'w') as f:
                    f.write(f'# Chapter {i+1}\n\n' + 'Word ' * 500)

            config = {
                'title': 'Test', 'author': 'Author',
                'manuscript': 'chapters/',
            }
            with open('book.yaml', 'w') as f:
                yaml.dump(config, f)

            result = runner.invoke(main, ['validate'])
            assert result.exit_code == 0


class TestCLIBuild:
    """Tests for the build command."""

    def test_build_missing_config(self, runner, tmp_dir):
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            result = runner.invoke(main, ['build'])
            assert result.exit_code != 0
            assert 'Error' in result.output

    def test_build_missing_manuscript(self, runner, tmp_dir):
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            config = {'title': 'Test', 'manuscript': 'nonexistent/'}
            with open('book.yaml', 'w') as f:
                yaml.dump(config, f)

            result = runner.invoke(main, ['build'])
            assert result.exit_code != 0


class TestCLIHelp:
    """Tests for help output."""

    def test_main_help(self, runner):
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'Book Formatter' in result.output

    def test_build_help(self, runner):
        result = runner.invoke(main, ['build', '--help'])
        assert result.exit_code == 0
        assert '--format' in result.output

    def test_init_help(self, runner):
        result = runner.invoke(main, ['init', '--help'])
        assert result.exit_code == 0
        assert '--title' in result.output

    def test_validate_help(self, runner):
        result = runner.invoke(main, ['validate', '--help'])
        assert result.exit_code == 0
