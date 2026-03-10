"""Tests for the paperback PDF generator."""

import os
import shutil
import pytest

from book_formatter.generators.pdf_paperback import (
    PaperbackPDFGenerator,
    _latex_escape,
    HEADER_TEMPLATE,
    TITLE_TEMPLATE,
)
from book_formatter.generators.base import GeneratorError
from book_formatter.parsers.ast_model import Book, Chapter
from book_formatter.config import BookConfig


class TestLatexEscape:
    """Tests for LaTeX special character escaping."""

    def test_ampersand(self):
        assert _latex_escape('Tom & Jerry') == r'Tom \& Jerry'

    def test_percent(self):
        assert _latex_escape('100%') == r'100\%'

    def test_dollar(self):
        assert _latex_escape('$100') == r'\$100'

    def test_hash(self):
        assert _latex_escape('#1') == r'\#1'

    def test_underscore(self):
        assert _latex_escape('my_var') == r'my\_var'

    def test_empty_string(self):
        assert _latex_escape('') == ''

    def test_none(self):
        assert _latex_escape(None) == ''

    def test_no_special_chars(self):
        assert _latex_escape('Hello World') == 'Hello World'

    def test_multiple_specials(self):
        assert _latex_escape('a & b $ c') == r'a \& b \$ c'


class TestHeaderTemplate:
    """Tests for the LaTeX header template."""

    def test_substitution(self):
        result = HEADER_TEMPLATE.substitute(
            header_left='Test Author',
            header_right='Test Title',
        )
        assert 'Test Author' in result
        assert 'Test Title' in result
        assert r'\fancyhf{}' in result

    def test_contains_fancyhdr(self):
        result = HEADER_TEMPLATE.substitute(
            header_left='A', header_right='B',
        )
        assert r'\usepackage{fancyhdr}' in result
        assert r'\pagestyle{bookstyle}' in result

    def test_widows_orphans(self):
        result = HEADER_TEMPLATE.substitute(
            header_left='A', header_right='B',
        )
        assert r'\widowpenalty=10000' in result
        assert r'\clubpenalty=10000' in result


class TestTitleTemplate:
    """Tests for the LaTeX title page template."""

    def test_substitution(self):
        result = TITLE_TEMPLATE.substitute(
            title='My Book',
            subtitle_block='',
            author='Jane Smith',
            website_block='',
            year=2026,
        )
        assert 'My Book' in result
        assert 'Jane Smith' in result
        assert '2026' in result

    def test_contains_titlepage(self):
        result = TITLE_TEMPLATE.substitute(
            title='T', subtitle_block='', author='A',
            website_block='', year=2026,
        )
        assert r'\begin{titlepage}' in result
        assert r'\end{titlepage}' in result

    def test_copyright_notice(self):
        result = TITLE_TEMPLATE.substitute(
            title='T', subtitle_block='', author='A',
            website_block='', year=2026,
        )
        assert 'All rights reserved' in result
        assert 'work of fiction' in result


class TestPaperbackPDFGenerator:
    """Tests for PaperbackPDFGenerator."""

    def test_format_name(self, sample_config, sample_book):
        gen = PaperbackPDFGenerator(sample_config, sample_book)
        assert gen.format_name == 'paperback'
        assert gen.file_extension == 'pdf'

    def test_trim_key_from_config(self, sample_config, sample_book):
        gen = PaperbackPDFGenerator(sample_config, sample_book)
        assert gen.trim_key == '5.5x8.5'

    def test_trim_key_override(self, sample_config, sample_book):
        gen = PaperbackPDFGenerator(sample_config, sample_book, trim='6x9')
        assert gen.trim_key == '6x9'

    @pytest.mark.skipif(
        not shutil.which('pandoc') or not shutil.which('xelatex'),
        reason='Pandoc and XeLaTeX required for build test'
    )
    def test_build_produces_pdf(self, sample_config, sample_book):
        gen = PaperbackPDFGenerator(sample_config, sample_book)
        output = gen.build()
        assert os.path.exists(output)
        assert output.endswith('.pdf')
        assert os.path.getsize(output) > 0

    def test_build_without_pandoc_raises(self, sample_config, sample_book, monkeypatch):
        monkeypatch.setattr('shutil.which', lambda x: None)
        gen = PaperbackPDFGenerator(sample_config, sample_book)
        with pytest.raises(GeneratorError, match='Pandoc'):
            gen.build()
