"""Tests for the AST model (Book, Chapter)."""

from book_formatter.parsers.ast_model import Book, Chapter


class TestChapter:
    """Tests for the Chapter dataclass."""

    def test_defaults(self):
        ch = Chapter(number=1, title='Test', content='Content')
        assert ch.number == 1
        assert ch.title == 'Test'
        assert ch.content == 'Content'
        assert ch.source_file == ''
        assert ch.word_count == 0
        assert ch.is_epilogue is False
        assert ch.is_preview is False
        assert ch.is_unnumbered is False

    def test_all_fields(self):
        ch = Chapter(
            number=5,
            title='Epilogue',
            content='Final words.',
            source_file='05_EPILOGUE.md',
            word_count=2,
            is_epilogue=True,
            is_preview=False,
            is_unnumbered=True,
        )
        assert ch.number == 5
        assert ch.is_epilogue is True
        assert ch.is_unnumbered is True


class TestBook:
    """Tests for the Book dataclass."""

    def test_empty_book(self):
        book = Book()
        assert len(book.chapters) == 0
        assert book.word_count == 0
        assert book.estimated_pages == 0

    def test_calculate_stats(self):
        chapters = [
            Chapter(number=1, title='A', content='x', word_count=500),
            Chapter(number=2, title='B', content='x', word_count=750),
        ]
        book = Book(chapters=chapters)
        book.calculate_stats()
        assert book.word_count == 1250
        assert book.estimated_pages == 5  # 1250 // 250

    def test_calculate_stats_custom_wpp(self):
        chapters = [
            Chapter(number=1, title='A', content='x', word_count=1000),
        ]
        book = Book(chapters=chapters)
        book.calculate_stats(words_per_page=200)
        assert book.estimated_pages == 5  # 1000 // 200

    def test_minimum_one_page(self):
        chapters = [
            Chapter(number=1, title='A', content='x', word_count=10),
        ]
        book = Book(chapters=chapters)
        book.calculate_stats()
        assert book.estimated_pages == 1

    def test_zero_chapters(self):
        book = Book()
        book.calculate_stats()
        assert book.word_count == 0
        assert book.estimated_pages == 1  # max(1, 0) = 1
