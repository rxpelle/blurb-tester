"""Tests for content structure analyzer."""

import pytest
from geo_optimizer.analyzers.content import analyze_content


class TestDirectAnswers:
    def test_good_direct_answers(self, good_blog_post):
        result = analyze_content(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Direct Answers')
        assert check['status'] in ('pass', 'warn')
        assert check['score'] > 0

    def test_poor_content_no_headings(self, poor_blog_post):
        result = analyze_content(poor_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Direct Answers')
        assert check['status'] == 'fail'
        assert check['score'] == 0

    def test_empty_content(self):
        result = analyze_content('')
        check = next(c for c in result.checks if c['name'] == 'Direct Answers')
        assert check['status'] == 'fail'

    def test_headings_with_long_answers(self):
        text = '## Question One?\n\n' + ('word ' * 100) + '\n\n## Question Two?\n\n' + ('word ' * 100)
        result = analyze_content(text)
        check = next(c for c in result.checks if c['name'] == 'Direct Answers')
        # Long answers (100 words) are outside 15-80 range
        assert check['score'] == 0


class TestQuestionHeadings:
    def test_question_headings_detected(self, good_blog_post):
        result = analyze_content(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Question Headings')
        assert check['status'] == 'pass'
        assert check['score'] == 10

    def test_no_question_headings(self, poor_blog_post):
        result = analyze_content(poor_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Question Headings')
        assert check['status'] == 'fail'
        assert check['score'] == 0

    def test_implied_question_headings(self):
        text = '## How to Build a Website\n\nContent here.\n\n## Why Python Is Popular\n\nMore content.\n\n## When to Use Docker\n\nEven more.'
        result = analyze_content(text)
        check = next(c for c in result.checks if c['name'] == 'Question Headings')
        assert check['status'] == 'pass'

    def test_single_question_heading(self):
        text = '## What is Python?\n\nPython is a language.'
        result = analyze_content(text)
        check = next(c for c in result.checks if c['name'] == 'Question Headings')
        assert check['status'] == 'warn'


class TestParagraphLength:
    def test_ideal_paragraphs(self, good_blog_post):
        result = analyze_content(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Paragraph Length')
        # Good blog post should have reasonable paragraph lengths
        assert check['score'] > 0

    def test_no_paragraphs(self):
        result = analyze_content('')
        check = next(c for c in result.checks if c['name'] == 'Paragraph Length')
        assert check['status'] == 'fail'

    def test_very_long_paragraphs(self):
        # Create content with extremely long paragraphs (>80 words each)
        long_para = ' '.join(['word'] * 150)
        text = f'{long_para}\n\n{long_para}\n\n{long_para}\n\n{long_para}'
        result = analyze_content(text)
        check = next(c for c in result.checks if c['name'] == 'Paragraph Length')
        assert check['status'] in ('warn', 'fail')


class TestKeyTakeaways:
    def test_key_takeaways_present(self, good_blog_post):
        result = analyze_content(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Key Takeaways')
        assert check['status'] == 'pass'
        assert check['score'] == 10

    def test_no_takeaways(self, poor_blog_post):
        result = analyze_content(poor_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Key Takeaways')
        assert check['status'] == 'fail'

    def test_tldr_section(self):
        text = '## Some Content\n\nBlah blah.\n\n## TL;DR\n\n- Point one\n- Point two\n- Point three'
        result = analyze_content(text)
        check = next(c for c in result.checks if c['name'] == 'Key Takeaways')
        assert check['status'] == 'pass'

    def test_bullet_list_without_heading(self):
        text = '## Content\n\nSome text.\n\n- Point one\n- Point two\n- Point three\n- Point four'
        result = analyze_content(text)
        check = next(c for c in result.checks if c['name'] == 'Key Takeaways')
        assert check['status'] == 'warn'


class TestScannableStructure:
    def test_good_structure(self, good_blog_post):
        result = analyze_content(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Scannable Structure')
        assert check['score'] > 0

    def test_no_headings(self, poor_blog_post):
        result = analyze_content(poor_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Scannable Structure')
        assert check['status'] == 'fail'

    def test_too_many_headings(self):
        # "Short para." is only 2 words, won't pass the >=3 words filter in _get_paragraphs
        # Use longer paragraphs so they're counted
        text = '\n'.join([f'## Heading {i}\n\nThis is a short paragraph.' for i in range(20)])
        result = analyze_content(text)
        check = next(c for c in result.checks if c['name'] == 'Scannable Structure')
        # Ratio ~1:1, within the 1-8 warn range
        assert check['status'] in ('pass', 'warn')


class TestListTableUsage:
    def test_lists_and_tables(self, good_blog_post):
        result = analyze_content(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Lists & Tables')
        assert check['status'] == 'pass'
        assert check['score'] == 10

    def test_no_lists_or_tables(self, poor_blog_post):
        result = analyze_content(poor_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Lists & Tables')
        assert check['status'] == 'fail'
        assert check['score'] == 0

    def test_lists_only(self):
        text = '## Content\n\nSome text.\n\n- Item one\n- Item two\n- Item three\n- Item four'
        result = analyze_content(text)
        check = next(c for c in result.checks if c['name'] == 'Lists & Tables')
        assert check['status'] == 'warn'
        assert check['score'] > 0


class TestOverall:
    def test_good_scores_higher_than_poor(self, good_blog_post, poor_blog_post):
        good_result = analyze_content(good_blog_post)
        poor_result = analyze_content(poor_blog_post)
        assert good_result.percentage > poor_result.percentage

    def test_max_score_is_60(self, good_blog_post):
        result = analyze_content(good_blog_post)
        assert result.max_score == 60.0

    def test_empty_content_returns_result(self):
        result = analyze_content('')
        assert result.category == 'content'
        assert len(result.checks) == 6
