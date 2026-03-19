"""Tests for structured data analyzer."""

import pytest
from geo_optimizer.analyzers.structured_data import analyze_structured_data


class TestJsonLdDetection:
    def test_json_ld_found_in_html(self, page_with_schema):
        result = analyze_structured_data('', page_with_schema)
        check = next(c for c in result.checks if c['name'] == 'JSON-LD Presence')
        assert check['status'] == 'pass'
        assert check['score'] == 10

    def test_no_json_ld_in_html(self, page_without_schema):
        result = analyze_structured_data('', page_without_schema)
        check = next(c for c in result.checks if c['name'] == 'JSON-LD Presence')
        assert check['status'] == 'fail'
        assert check['score'] == 0

    def test_markdown_file_warns(self):
        result = analyze_structured_data('# Hello\n\nSome content.', None)
        check = next(c for c in result.checks if c['name'] == 'JSON-LD Presence')
        assert check['status'] == 'warn'

    def test_invalid_json_ld(self):
        html = '<html><head><script type="application/ld+json">{invalid json here</script></head><body></body></html>'
        result = analyze_structured_data('', html)
        check = next(c for c in result.checks if c['name'] == 'JSON-LD Presence')
        assert check['status'] == 'fail'
        assert 'invalid' in check['detail'].lower()


class TestBookSchemaValidation:
    def test_complete_book_schema(self, book_landing_page):
        result = analyze_structured_data('', book_landing_page)
        check = next(c for c in result.checks if c['name'] == 'Required Fields')
        assert check['status'] == 'pass'

    def test_incomplete_book_schema(self):
        html = '''<html><head>
        <script type="application/ld+json">
        {"@context": "https://schema.org", "@type": "Book", "name": "Test Book"}
        </script>
        </head><body></body></html>'''
        result = analyze_structured_data('', html)
        check = next(c for c in result.checks if c['name'] == 'Required Fields')
        assert check['status'] in ('warn', 'fail')
        assert 'missing' in check['detail'].lower()


class TestArticleSchemaValidation:
    def test_complete_article_schema(self, page_with_schema):
        result = analyze_structured_data('', page_with_schema)
        check = next(c for c in result.checks if c['name'] == 'Required Fields')
        assert check['status'] == 'pass'

    def test_article_missing_fields(self):
        html = '''<html><head>
        <script type="application/ld+json">
        {"@context": "https://schema.org", "@type": "Article", "headline": "Test"}
        </script>
        </head><body></body></html>'''
        result = analyze_structured_data('', html)
        check = next(c for c in result.checks if c['name'] == 'Required Fields')
        assert check['status'] in ('warn', 'fail')


class TestFAQPageValidation:
    def test_faq_schema_detected(self, page_with_schema):
        result = analyze_structured_data('', page_with_schema)
        check = next(c for c in result.checks if c['name'] == 'Schema Types')
        assert check['status'] == 'pass'
        assert 'FAQPage' in check['detail']


class TestSchemaTypes:
    def test_multiple_types(self, page_with_schema):
        result = analyze_structured_data('', page_with_schema)
        check = next(c for c in result.checks if c['name'] == 'Schema Types')
        assert check['status'] == 'pass'

    def test_no_types(self, page_without_schema):
        result = analyze_structured_data('', page_without_schema)
        check = next(c for c in result.checks if c['name'] == 'Schema Types')
        assert check['status'] == 'fail'


class TestAuthorMarkup:
    def test_author_as_person_object(self, page_with_schema):
        result = analyze_structured_data('', page_with_schema)
        check = next(c for c in result.checks if c['name'] == 'Author Markup')
        assert check['status'] == 'pass'

    def test_author_as_string(self):
        html = '''<html><head>
        <script type="application/ld+json">
        {"@context": "https://schema.org", "@type": "Article", "author": "John Doe"}
        </script>
        </head><body></body></html>'''
        result = analyze_structured_data('', html)
        check = next(c for c in result.checks if c['name'] == 'Author Markup')
        assert check['status'] == 'warn'

    def test_no_author(self):
        html = '''<html><head>
        <script type="application/ld+json">
        {"@context": "https://schema.org", "@type": "Article", "headline": "Test"}
        </script>
        </head><body></body></html>'''
        result = analyze_structured_data('', html)
        check = next(c for c in result.checks if c['name'] == 'Author Markup')
        assert check['status'] == 'fail'


class TestBreadcrumb:
    def test_breadcrumb_present(self, book_landing_page):
        result = analyze_structured_data('', book_landing_page)
        check = next(c for c in result.checks if c['name'] == 'Breadcrumb Markup')
        assert check['status'] == 'pass'

    def test_no_breadcrumb(self, page_with_schema):
        result = analyze_structured_data('', page_with_schema)
        check = next(c for c in result.checks if c['name'] == 'Breadcrumb Markup')
        assert check['status'] == 'fail'

    def test_markdown_breadcrumb_warning(self):
        result = analyze_structured_data('# Test', None)
        check = next(c for c in result.checks if c['name'] == 'Breadcrumb Markup')
        assert check['status'] == 'warn'


class TestOverall:
    def test_max_score_is_50(self, page_with_schema):
        result = analyze_structured_data('', page_with_schema)
        assert result.max_score == 50.0

    def test_category_name(self, page_with_schema):
        result = analyze_structured_data('', page_with_schema)
        assert result.category == 'structured_data'
