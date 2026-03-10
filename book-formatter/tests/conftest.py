"""Shared fixtures for book-formatter tests."""

import os
import tempfile
import shutil

import pytest
import yaml

from book_formatter.config import BookConfig, load_config
from book_formatter.parsers.ast_model import Book, Chapter


@pytest.fixture
def tmp_dir():
    """Create a temporary directory, cleaned up after test."""
    d = tempfile.mkdtemp(prefix='book_formatter_test_')
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_chapter_dir(tmp_dir):
    """Create a directory with sample numbered markdown chapter files."""
    chapters_dir = os.path.join(tmp_dir, 'chapters')
    os.makedirs(chapters_dir)

    chapters = {
        '01_THE_BEGINNING.md': '# The Beginning\n\nIt was a dark and stormy night. ' * 20,
        '02_THE_MIDDLE.md': '# The Middle\n\nThings got complicated. ' * 25,
        '03_THE_END.md': '# The End\n\nEverything resolved. ' * 15,
    }
    for filename, content in chapters.items():
        with open(os.path.join(chapters_dir, filename), 'w') as f:
            f.write(content)

    return chapters_dir


@pytest.fixture
def sample_single_md(tmp_dir):
    """Create a single markdown file with multiple chapters."""
    filepath = os.path.join(tmp_dir, 'manuscript.md')
    content = """# The Beginning

It was a dark and stormy night. The wind howled through the trees. Nobody expected what came next. The old house creaked and groaned under the weight of years. Sarah pulled her coat tighter and stepped inside.

# The Middle

Things got complicated when the letter arrived. It bore the seal of the ancient order. Marcus read it twice before understanding dawned on his face. They had been watching all along.

# The Epilogue

And so it ended, not with a bang but with a whisper. The survivors gathered at dawn, counting their losses and their blessings in equal measure. The world would never be the same.
"""
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath


@pytest.fixture
def sample_config_yaml(tmp_dir, sample_chapter_dir):
    """Create a sample book.yaml config file."""
    config = {
        'title': 'Test Book',
        'subtitle': 'A Test Subtitle',
        'author': 'Test Author',
        'website': 'testauthor.com',
        'year': 2026,
        'manuscript': 'chapters/',
        'chapter_pattern': '[0-9][0-9]_*.md',
        'output': 'output',
        'print': {
            'trim': '5.5x8.5',
        },
        'typography': {
            'body_font': 'Palatino',
            'heading_font': 'Palatino',
            'body_size': '11pt',
            'line_spacing': 1.3,
        },
    }
    config_path = os.path.join(tmp_dir, 'book.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    return config_path


@pytest.fixture
def sample_book():
    """Create a sample Book object for generator tests."""
    chapters = [
        Chapter(number=1, title='The Beginning', content='# The Beginning\n\nIt was a dark and stormy night. ' * 20,
                source_file='01_THE_BEGINNING.md', word_count=160),
        Chapter(number=2, title='The Middle', content='# The Middle\n\nThings got complicated. ' * 25,
                source_file='02_THE_MIDDLE.md', word_count=100),
        Chapter(number=3, title='The End', content='# The End\n\nEverything resolved. ' * 15,
                source_file='03_THE_END.md', word_count=60),
    ]
    book = Book(chapters=chapters)
    book.calculate_stats()
    return book


@pytest.fixture
def sample_config(tmp_dir):
    """Create a BookConfig object for generator tests."""
    config = BookConfig()
    config.title = 'Test Book'
    config.subtitle = 'A Test Subtitle'
    config.author = 'Test Author'
    config.year = 2026
    config.output = os.path.join(tmp_dir, 'output')
    config._config_dir = tmp_dir
    config.typography.body_font = 'Palatino'
    config.typography.heading_font = 'Palatino'
    return config
