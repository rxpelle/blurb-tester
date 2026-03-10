"""Tests for book configuration loading and validation."""

import os
import pytest
import yaml

from book_formatter.config import (
    BookConfig,
    SeriesInfo,
    ISBNInfo,
    PrintSettings,
    Typography,
    HeaderSettings,
    FrontMatterItem,
    BackMatterItem,
    TRIM_SIZES,
    load_config,
    generate_example_config,
)


class TestBookConfigDefaults:
    """Tests for default BookConfig values."""

    def test_default_title(self):
        config = BookConfig()
        assert config.title == 'Untitled'

    def test_default_author(self):
        config = BookConfig()
        assert config.author == 'Unknown Author'

    def test_default_trim(self):
        config = BookConfig()
        assert config.print_settings.trim == '5.5x8.5'

    def test_default_typography(self):
        config = BookConfig()
        assert config.typography.body_size == '11pt'
        assert config.typography.line_spacing == 1.3

    def test_default_chapter_pattern(self):
        config = BookConfig()
        assert config.chapter_pattern == '[0-9][0-9]_*.md'


class TestResolvePath:
    """Tests for path resolution relative to config directory."""

    def test_relative_path(self):
        config = BookConfig()
        config._config_dir = '/home/user/mybook'
        assert config.resolve_path('chapters/') == '/home/user/mybook/chapters/'

    def test_absolute_path_unchanged(self):
        config = BookConfig()
        config._config_dir = '/home/user/mybook'
        assert config.resolve_path('/tmp/chapters/') == '/tmp/chapters/'


class TestGetTrim:
    """Tests for trim size retrieval."""

    def test_paperback_trim(self):
        config = BookConfig()
        trim = config.get_trim('paperback')
        assert trim == TRIM_SIZES['5.5x8.5']

    def test_large_print_trim(self):
        config = BookConfig()
        trim = config.get_trim('large_print')
        assert trim == TRIM_SIZES['7x10']

    def test_hardcover_trim(self):
        config = BookConfig()
        trim = config.get_trim('hardcover')
        assert trim == TRIM_SIZES['6x9']

    def test_invalid_trim_raises(self):
        config = BookConfig()
        config.print_settings.trim = '99x99'
        with pytest.raises(ValueError, match='Unknown trim size'):
            config.get_trim('paperback')

    def test_all_trim_sizes_valid(self):
        for key, dims in TRIM_SIZES.items():
            assert len(dims) == 6
            assert all(isinstance(d, (int, float)) for d in dims)


class TestGetHeaders:
    """Tests for header template substitution."""

    def test_author_substitution(self):
        config = BookConfig()
        config.author = 'Jane Smith'
        assert config.get_header_left() == 'Jane Smith'

    def test_title_substitution(self):
        config = BookConfig()
        config.title = 'My Great Novel'
        assert config.get_header_right() == 'My Great Novel'

    def test_custom_header_template(self):
        config = BookConfig()
        config.title = 'Novel'
        config.author = 'Author'
        config.headers.left = '{title} by {author}'
        assert config.get_header_left() == 'Novel by Author'


class TestLoadConfig:
    """Tests for loading config from YAML files."""

    def test_load_simple_config(self, tmp_dir):
        config_data = {
            'title': 'My Book',
            'author': 'John Doe',
            'year': 2025,
        }
        path = os.path.join(tmp_dir, 'book.yaml')
        with open(path, 'w') as f:
            yaml.dump(config_data, f)

        config = load_config(path)
        assert config.title == 'My Book'
        assert config.author == 'John Doe'
        assert config.year == 2025

    def test_load_with_series(self, tmp_dir):
        config_data = {
            'title': 'Book 2',
            'series': {'name': 'The Trilogy', 'number': 2},
        }
        path = os.path.join(tmp_dir, 'book.yaml')
        with open(path, 'w') as f:
            yaml.dump(config_data, f)

        config = load_config(path)
        assert config.series.name == 'The Trilogy'
        assert config.series.number == 2

    def test_load_with_typography(self, tmp_dir):
        config_data = {
            'title': 'Styled Book',
            'typography': {
                'body_font': 'Palatino',
                'body_size': '12pt',
                'line_spacing': 1.5,
            },
        }
        path = os.path.join(tmp_dir, 'book.yaml')
        with open(path, 'w') as f:
            yaml.dump(config_data, f)

        config = load_config(path)
        assert config.typography.body_font == 'Palatino'
        assert config.typography.body_size == '12pt'
        assert config.typography.line_spacing == 1.5

    def test_load_with_print_settings(self, tmp_dir):
        config_data = {
            'title': 'Print Book',
            'print': {
                'trim': '6x9',
                'bleed': True,
            },
        }
        path = os.path.join(tmp_dir, 'book.yaml')
        with open(path, 'w') as f:
            yaml.dump(config_data, f)

        config = load_config(path)
        assert config.print_settings.trim == '6x9'
        assert config.print_settings.bleed is True

    def test_load_with_front_matter(self, tmp_dir):
        config_data = {
            'title': 'Book',
            'front_matter': [
                {'type': 'title_page'},
                {'type': 'dedication', 'text': 'To my family'},
            ],
        }
        path = os.path.join(tmp_dir, 'book.yaml')
        with open(path, 'w') as f:
            yaml.dump(config_data, f)

        config = load_config(path)
        assert len(config.front_matter) == 2
        assert config.front_matter[0].type == 'title_page'
        assert config.front_matter[1].text == 'To my family'

    def test_load_with_back_matter(self, tmp_dir):
        config_data = {
            'title': 'Book',
            'back_matter': [
                {'type': 'author_bio', 'text': 'About the author.'},
                {'type': 'also_by', 'books': ['Book 1', 'Book 2']},
            ],
        }
        path = os.path.join(tmp_dir, 'book.yaml')
        with open(path, 'w') as f:
            yaml.dump(config_data, f)

        config = load_config(path)
        assert len(config.back_matter) == 2
        assert config.back_matter[1].books == ['Book 1', 'Book 2']

    def test_missing_config_raises(self):
        with pytest.raises(FileNotFoundError, match='Config file not found'):
            load_config('/nonexistent/path/book.yaml')

    def test_empty_yaml_uses_defaults(self, tmp_dir):
        path = os.path.join(tmp_dir, 'book.yaml')
        with open(path, 'w') as f:
            f.write('')  # empty YAML

        config = load_config(path)
        assert config.title == 'Untitled'
        assert config.author == 'Unknown Author'

    def test_config_dir_set(self, tmp_dir):
        path = os.path.join(tmp_dir, 'book.yaml')
        with open(path, 'w') as f:
            yaml.dump({'title': 'Test'}, f)

        config = load_config(path)
        assert config._config_dir == tmp_dir


class TestGenerateExampleConfig:
    """Tests for example config generation."""

    def test_generates_valid_yaml(self):
        content = generate_example_config(title='My Book', author='Author')
        parsed = yaml.safe_load(content)
        assert parsed['title'] == 'My Book'
        assert parsed['author'] == 'Author'

    def test_default_values(self):
        content = generate_example_config()
        parsed = yaml.safe_load(content)
        assert parsed['title'] == 'My Book Title'
        assert parsed['author'] == 'Author Name'

    def test_style_included(self):
        content = generate_example_config(style='thriller')
        parsed = yaml.safe_load(content)
        assert parsed['style'] == 'thriller'

    def test_contains_comments(self):
        content = generate_example_config()
        assert '#' in content  # Has YAML comments


class TestTrimSizes:
    """Tests for trim size constants."""

    def test_standard_sizes_present(self):
        assert '5.5x8.5' in TRIM_SIZES
        assert '6x9' in TRIM_SIZES
        assert '7x10' in TRIM_SIZES

    def test_dimensions_reasonable(self):
        for key, (w, h, gutter, outside, top, bottom) in TRIM_SIZES.items():
            assert 4 <= w <= 10
            assert 7 <= h <= 11
            assert 0.5 <= gutter <= 1.5
            assert 0.3 <= outside <= 1.0
            assert 0.5 <= top <= 1.0
            assert 0.5 <= bottom <= 1.0
