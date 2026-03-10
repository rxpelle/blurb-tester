"""Tests for the base generator."""

import os
import pytest

from book_formatter.generators.base import BaseGenerator, GeneratorError
from book_formatter.parsers.ast_model import Book, Chapter
from book_formatter.config import BookConfig


class TestBaseGenerator:
    """Tests for BaseGenerator utility methods."""

    def test_ensure_output_dir_creates(self, sample_config, sample_book):
        gen = BaseGenerator(sample_config, sample_book)
        gen.ensure_output_dir()
        assert os.path.isdir(gen.output_dir)

    def test_output_path(self, sample_config, sample_book):
        gen = BaseGenerator(sample_config, sample_book)
        gen.file_extension = 'pdf'
        path = gen.output_path('paperback_5.5x8.5')
        assert path.endswith('Test_Book_paperback_5.5x8.5.pdf')

    def test_output_path_strips_colons(self, sample_config, sample_book):
        sample_config.title = 'Book: A Story'
        gen = BaseGenerator(sample_config, sample_book)
        gen.file_extension = 'epub'
        path = gen.output_path('ebook')
        assert ':' not in os.path.basename(path)

    def test_assemble_manuscript(self, sample_config, sample_book):
        gen = BaseGenerator(sample_config, sample_book)
        ms = gen.assemble_manuscript()
        assert 'The Beginning' in ms
        assert 'The Middle' in ms
        assert 'The End' in ms
        assert '\\newpage' in ms

    def test_assemble_manuscript_single_chapter(self, sample_config):
        book = Book(chapters=[
            Chapter(number=1, title='Only', content='# Only\n\nContent.')
        ])
        gen = BaseGenerator(sample_config, book)
        ms = gen.assemble_manuscript()
        assert '\\newpage' not in ms
        assert 'Content.' in ms

    def test_write_temp_manuscript(self, sample_config, sample_book):
        gen = BaseGenerator(sample_config, sample_book)
        path = gen.write_temp_manuscript('test content')
        try:
            assert os.path.exists(path)
            with open(path) as f:
                assert f.read() == 'test content'
        finally:
            os.unlink(path)

    def test_get_lua_filter_path(self, sample_config, sample_book):
        gen = BaseGenerator(sample_config, sample_book)
        path = gen.get_lua_filter_path('pagebreak.lua')
        assert path.endswith('lua_filters/pagebreak.lua')
        assert os.path.exists(path)

    def test_build_not_implemented(self, sample_config, sample_book):
        gen = BaseGenerator(sample_config, sample_book)
        with pytest.raises(NotImplementedError):
            gen.build()


class TestGeneratorError:
    """Tests for GeneratorError exception."""

    def test_is_exception(self):
        err = GeneratorError("test error")
        assert isinstance(err, Exception)
        assert str(err) == "test error"
