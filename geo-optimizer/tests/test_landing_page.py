"""Tests for landing page analyzer."""

import pytest
from geo_optimizer.analyzers.landing_page import analyze_landing_page
from bs4 import BeautifulSoup


class TestBookMetadata:
    def test_complete_metadata(self, book_landing_page):
        soup = BeautifulSoup(book_landing_page, 'html.parser')
        text = soup.get_text()
        result = analyze_landing_page(text, book_landing_page, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Book Metadata')
        assert check['status'] == 'pass'

    def test_minimal_metadata(self):
        text = 'The Book Title by Author Name'
        result = analyze_landing_page(text, None, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Book Metadata')
        assert check['status'] in ('warn', 'fail')


class TestComparisonPositioning:
    def test_comparison_found(self, book_landing_page):
        soup = BeautifulSoup(book_landing_page, 'html.parser')
        text = soup.get_text()
        result = analyze_landing_page(text, book_landing_page, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Comparison Positioning')
        assert check['status'] == 'pass'

    def test_no_comparison(self):
        text = 'This is a book about things. It has 300 pages. ISBN: 978-1234567890. Price: $9.99. Genre: thriller. Author: John Smith. Publication date: January 1, 2025.'
        result = analyze_landing_page(text, None, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Comparison Positioning')
        assert check['status'] == 'fail'


class TestReviewMarkup:
    def test_reviews_present(self, book_landing_page):
        soup = BeautifulSoup(book_landing_page, 'html.parser')
        text = soup.get_text()
        result = analyze_landing_page(text, book_landing_page, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Review Markup')
        assert check['score'] > 0

    def test_no_reviews(self):
        text = 'A book. 300 pages. ISBN: 978-1234567890. Price: $9.99. Genre: thriller. Author: Test. Publication date: January 1, 2025.'
        result = analyze_landing_page(text, None, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Review Markup')
        assert check['status'] == 'fail'


class TestNonBookPage:
    def test_non_book_page_neutral(self):
        text = 'This is a regular blog post about technology and science.'
        result = analyze_landing_page(text, None, is_book_page=False)
        assert result.score > 0  # Neutral, not zero
        assert len(result.checks) == 1
        assert 'skipped' in result.checks[0]['detail'].lower()

    def test_auto_detect_book_page(self, book_landing_page):
        soup = BeautifulSoup(book_landing_page, 'html.parser')
        text = soup.get_text()
        result = analyze_landing_page(text, book_landing_page, is_book_page=False)
        # Should auto-detect as book page due to ISBN, pages, etc.
        assert len(result.checks) > 1  # Not the single neutral check


class TestSeriesInfo:
    def test_series_detected(self, book_landing_page):
        soup = BeautifulSoup(book_landing_page, 'html.parser')
        text = soup.get_text()
        result = analyze_landing_page(text, book_landing_page, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Series Information')
        assert check['status'] == 'pass'

    def test_no_series(self):
        text = 'A standalone novel. 300 pages. ISBN: 978-1234567890. Price: $9.99. Genre: thriller. Author: Test. Publication date: January 1, 2025.'
        result = analyze_landing_page(text, None, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Series Information')
        assert check['status'] == 'warn'


class TestBuyLinks:
    def test_buy_links_found(self, book_landing_page):
        soup = BeautifulSoup(book_landing_page, 'html.parser')
        text = soup.get_text()
        result = analyze_landing_page(text, book_landing_page, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Buy Links')
        assert check['status'] == 'pass'


class TestAuthorBio:
    def test_author_bio_found(self, book_landing_page):
        soup = BeautifulSoup(book_landing_page, 'html.parser')
        text = soup.get_text()
        result = analyze_landing_page(text, book_landing_page, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Author Bio')
        assert check['status'] == 'pass'

    def test_no_author_bio(self):
        text = 'A book by someone. 300 pages. ISBN: 978-1234567890. Price: $9.99. Genre: thriller. Author: Test. Publication date: January 1, 2025.'
        result = analyze_landing_page(text, None, is_book_page=True)
        check = next(c for c in result.checks if c['name'] == 'Author Bio')
        assert check['status'] == 'fail'
