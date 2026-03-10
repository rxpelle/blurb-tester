"""Tests for the EPUB generator."""

import os
import shutil
import pytest

from book_formatter.generators.epub_standard import StandardEPUBGenerator
from book_formatter.generators.base import GeneratorError
from book_formatter.parsers.ast_model import Book, Chapter
from book_formatter.config import BookConfig


class TestStandardEPUBGenerator:
    """Tests for StandardEPUBGenerator."""

    def test_format_name(self, sample_config, sample_book):
        gen = StandardEPUBGenerator(sample_config, sample_book)
        assert gen.format_name == 'epub'
        assert gen.file_extension == 'epub'

    def test_css_path_default(self, sample_config, sample_book):
        gen = StandardEPUBGenerator(sample_config, sample_book)
        css = gen._get_css_path()
        assert css.endswith('epub.css')
        assert os.path.exists(css)

    def test_css_path_nonexistent_style_falls_back(self, sample_config, sample_book):
        sample_config.style = 'nonexistent'
        gen = StandardEPUBGenerator(sample_config, sample_book)
        css = gen._get_css_path()
        assert 'default' in css

    def test_resolve_cover_empty(self, sample_config, sample_book):
        sample_config.cover = ''
        gen = StandardEPUBGenerator(sample_config, sample_book)
        assert gen._resolve_cover() == ''

    def test_resolve_cover_missing_file(self, sample_config, sample_book):
        sample_config.cover = 'nonexistent.jpg'
        gen = StandardEPUBGenerator(sample_config, sample_book)
        assert gen._resolve_cover() == ''

    def test_resolve_cover_existing(self, sample_config, sample_book, tmp_dir):
        cover_path = os.path.join(tmp_dir, 'cover.jpg')
        with open(cover_path, 'wb') as f:
            f.write(b'\xff\xd8\xff')  # minimal JPEG header
        sample_config.cover = 'cover.jpg'
        gen = StandardEPUBGenerator(sample_config, sample_book)
        assert gen._resolve_cover() == cover_path

    @pytest.mark.skipif(
        not shutil.which('pandoc'),
        reason='Pandoc required for build test'
    )
    def test_build_produces_epub(self, sample_config, sample_book):
        gen = StandardEPUBGenerator(sample_config, sample_book)
        output = gen.build()
        assert os.path.exists(output)
        assert output.endswith('.epub')
        assert os.path.getsize(output) > 0

    def test_build_without_pandoc_raises(self, sample_config, sample_book, monkeypatch):
        monkeypatch.setattr('shutil.which', lambda x: None)
        gen = StandardEPUBGenerator(sample_config, sample_book)
        with pytest.raises(GeneratorError, match='Pandoc'):
            gen.build()
