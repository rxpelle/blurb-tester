"""Tests for the markdown manuscript parser."""

import os
import pytest

from book_formatter.parsers.markdown import (
    parse_manuscript,
    _parse_directory,
    _parse_single_file,
    _parse_chapter_file,
    _detect_special_chapter,
)
from book_formatter.parsers.ast_model import Book, Chapter
from book_formatter.config import BookConfig


class TestParseDirectory:
    """Tests for parsing a directory of numbered chapter files."""

    def test_parses_all_chapters(self, sample_chapter_dir):
        book = _parse_directory(sample_chapter_dir, '[0-9][0-9]_*.md')
        assert len(book.chapters) == 3

    def test_chapters_sorted_by_filename(self, sample_chapter_dir):
        book = _parse_directory(sample_chapter_dir, '[0-9][0-9]_*.md')
        assert book.chapters[0].title == 'The Beginning'
        assert book.chapters[1].title == 'The Middle'
        assert book.chapters[2].title == 'The End'

    def test_chapter_numbers_from_filenames(self, sample_chapter_dir):
        book = _parse_directory(sample_chapter_dir, '[0-9][0-9]_*.md')
        assert book.chapters[0].number == 1
        assert book.chapters[1].number == 2
        assert book.chapters[2].number == 3

    def test_word_counts_calculated(self, sample_chapter_dir):
        book = _parse_directory(sample_chapter_dir, '[0-9][0-9]_*.md')
        for ch in book.chapters:
            assert ch.word_count > 0

    def test_book_stats_calculated(self, sample_chapter_dir):
        book = _parse_directory(sample_chapter_dir, '[0-9][0-9]_*.md')
        assert book.word_count > 0
        assert book.estimated_pages > 0
        assert book.word_count == sum(ch.word_count for ch in book.chapters)

    def test_empty_directory_raises(self, tmp_dir):
        empty_dir = os.path.join(tmp_dir, 'empty')
        os.makedirs(empty_dir)
        with pytest.raises(FileNotFoundError, match='No chapter files'):
            _parse_directory(empty_dir, '[0-9][0-9]_*.md')

    def test_no_matching_pattern_raises(self, sample_chapter_dir):
        with pytest.raises(FileNotFoundError, match='No chapter files'):
            _parse_directory(sample_chapter_dir, 'nonexistent_*.md')

    def test_source_file_tracked(self, sample_chapter_dir):
        book = _parse_directory(sample_chapter_dir, '[0-9][0-9]_*.md')
        for ch in book.chapters:
            assert ch.source_file.endswith('.md')
            assert os.path.exists(ch.source_file)


class TestParseSingleFile:
    """Tests for parsing a single markdown file with # headings."""

    def test_splits_on_h1_headings(self, sample_single_md):
        book = _parse_single_file(sample_single_md)
        assert len(book.chapters) == 3

    def test_chapter_titles_extracted(self, sample_single_md):
        book = _parse_single_file(sample_single_md)
        assert book.chapters[0].title == 'The Beginning'
        assert book.chapters[1].title == 'The Middle'
        assert book.chapters[2].title == 'The Epilogue'

    def test_epilogue_detected(self, sample_single_md):
        book = _parse_single_file(sample_single_md)
        epilogue = book.chapters[2]
        assert epilogue.is_epilogue is True
        assert epilogue.is_unnumbered is True

    def test_chapter_content_preserved(self, sample_single_md):
        book = _parse_single_file(sample_single_md)
        assert 'dark and stormy night' in book.chapters[0].content
        assert 'letter arrived' in book.chapters[1].content

    def test_sequential_numbering(self, sample_single_md):
        book = _parse_single_file(sample_single_md)
        for i, ch in enumerate(book.chapters):
            assert ch.number == i + 1

    def test_word_counts(self, sample_single_md):
        book = _parse_single_file(sample_single_md)
        for ch in book.chapters:
            assert ch.word_count > 0

    def test_anchor_attributes_stripped(self, tmp_dir):
        filepath = os.path.join(tmp_dir, 'test.md')
        with open(filepath, 'w') as f:
            f.write('# My Chapter {#chapter-1}\n\nSome content here.\n')
        book = _parse_single_file(filepath)
        assert book.chapters[0].title == 'My Chapter'


class TestParseChapterFile:
    """Tests for parsing individual chapter files."""

    def test_extracts_number_and_title(self, tmp_dir):
        filepath = os.path.join(tmp_dir, '05_THE_GREAT_ESCAPE.md')
        with open(filepath, 'w') as f:
            f.write('Content of the chapter.')
        ch = _parse_chapter_file(filepath, 1)
        assert ch.number == 5
        assert ch.title == 'The Great Escape'

    def test_title_case_articles(self, tmp_dir):
        filepath = os.path.join(tmp_dir, '01_THE_LORD_OF_THE_RINGS.md')
        with open(filepath, 'w') as f:
            f.write('Content.')
        ch = _parse_chapter_file(filepath, 1)
        # "The" at start stays capitalized, "of" and "the" mid-title lowercase
        assert 'of the' in ch.title.lower()

    def test_fallback_number_when_no_prefix(self, tmp_dir):
        filepath = os.path.join(tmp_dir, 'PROLOGUE.md')
        with open(filepath, 'w') as f:
            f.write('Prologue content.')
        ch = _parse_chapter_file(filepath, 7)
        assert ch.number == 7

    def test_end_chapter_markers_stripped(self, tmp_dir):
        filepath = os.path.join(tmp_dir, '01_TEST.md')
        with open(filepath, 'w') as f:
            f.write('Chapter content.\n\n---\n\nEND CHAPTER 1\n')
        ch = _parse_chapter_file(filepath, 1)
        assert 'END CHAPTER' not in ch.content


class TestDetectSpecialChapter:
    """Tests for special chapter type detection."""

    def test_epilogue_detected(self):
        ch = Chapter(number=1, title='Epilogue', content='')
        _detect_special_chapter(ch)
        assert ch.is_epilogue is True
        assert ch.is_unnumbered is True

    def test_prologue_detected(self):
        ch = Chapter(number=1, title='Prologue', content='')
        _detect_special_chapter(ch)
        assert ch.is_unnumbered is True
        assert ch.is_epilogue is False

    def test_preview_detected(self):
        ch = Chapter(number=1, title='Preview of Book 2', content='')
        _detect_special_chapter(ch)
        assert ch.is_preview is True
        assert ch.is_unnumbered is True

    def test_normal_chapter_unchanged(self):
        ch = Chapter(number=1, title='The Storm', content='')
        _detect_special_chapter(ch)
        assert ch.is_epilogue is False
        assert ch.is_preview is False
        assert ch.is_unnumbered is False

    def test_case_insensitive(self):
        ch = Chapter(number=1, title='THE EPILOGUE', content='')
        _detect_special_chapter(ch)
        assert ch.is_epilogue is True


class TestParseManuscript:
    """Integration tests for parse_manuscript with config."""

    def test_directory_mode(self, sample_config_yaml):
        config = BookConfig()
        config_dir = os.path.dirname(sample_config_yaml)
        config._config_dir = config_dir
        config.manuscript = 'chapters/'
        config.chapter_pattern = '[0-9][0-9]_*.md'

        book = parse_manuscript(config)
        assert len(book.chapters) == 3

    def test_single_file_mode(self, sample_single_md):
        config = BookConfig()
        config._config_dir = os.path.dirname(sample_single_md)
        config.manuscript = os.path.basename(sample_single_md)

        book = parse_manuscript(config)
        assert len(book.chapters) == 3

    def test_missing_manuscript_raises(self, tmp_dir):
        config = BookConfig()
        config._config_dir = tmp_dir
        config.manuscript = 'nonexistent/'

        with pytest.raises(FileNotFoundError, match='Manuscript not found'):
            parse_manuscript(config)
