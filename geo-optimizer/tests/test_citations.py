"""Tests for citations analyzer."""

import pytest
from geo_optimizer.analyzers.citations import analyze_citations


class TestExternalLinks:
    def test_good_external_links(self, good_blog_post):
        result = analyze_citations(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'External Links')
        assert check['status'] == 'pass'
        assert check['score'] > 0

    def test_no_links(self, poor_blog_post):
        result = analyze_citations(poor_blog_post)
        check = next(c for c in result.checks if c['name'] == 'External Links')
        assert check['status'] == 'fail'
        assert check['score'] == 0

    def test_few_links(self):
        text = 'Check out [this](https://example.com) for more info.'
        result = analyze_citations(text)
        check = next(c for c in result.checks if c['name'] == 'External Links')
        assert check['status'] == 'warn'

    def test_many_links(self):
        links = '\n'.join([f'[link{i}](https://example{i}.com)' for i in range(15)])
        result = analyze_citations(links)
        check = next(c for c in result.checks if c['name'] == 'External Links')
        assert check['status'] == 'warn'
        assert 'trimming' in check['detail'].lower()


class TestLinkQuality:
    def test_high_quality_links(self, good_blog_post):
        result = analyze_citations(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Link Quality')
        assert check['status'] == 'pass'
        assert check['score'] > 0

    def test_no_links_for_quality(self, poor_blog_post):
        result = analyze_citations(poor_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Link Quality')
        assert check['status'] == 'fail'

    def test_edu_gov_links(self):
        text = '[NIH](https://www.nih.gov/study) and [Harvard](https://www.harvard.edu/research)'
        result = analyze_citations(text)
        check = next(c for c in result.checks if c['name'] == 'Link Quality')
        assert check['status'] == 'pass'

    def test_generic_links_only(self):
        text = '[Blog](https://randomblog.com) and [Site](https://randomsite.net) and [Shop](https://myshop.io)'
        result = analyze_citations(text)
        check = next(c for c in result.checks if c['name'] == 'Link Quality')
        assert check['status'] == 'fail'


class TestSourceAttribution:
    def test_good_attributions(self, good_blog_post):
        result = analyze_citations(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Source Attribution')
        assert check['status'] == 'pass'

    def test_no_attributions(self):
        text = 'This is a fact. Here is another fact. Nothing is cited.'
        result = analyze_citations(text)
        check = next(c for c in result.checks if c['name'] == 'Source Attribution')
        assert check['status'] == 'fail'

    def test_single_attribution(self):
        text = 'According to recent findings, the data shows improvement.'
        result = analyze_citations(text)
        check = next(c for c in result.checks if c['name'] == 'Source Attribution')
        assert check['status'] == 'warn'


class TestDataCitations:
    def test_rich_data_citations(self, good_blog_post):
        result = analyze_citations(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Data Citations')
        assert check['status'] == 'pass'

    def test_no_data(self):
        text = 'There are many things happening and stuff is interesting.'
        result = analyze_citations(text)
        check = next(c for c in result.checks if c['name'] == 'Data Citations')
        assert check['status'] == 'fail'

    def test_statistics_detected(self):
        text = 'The market grew by 45% in 2023. Revenue reached $2 billion according to NIH data.'
        result = analyze_citations(text)
        check = next(c for c in result.checks if c['name'] == 'Data Citations')
        assert check['score'] > 0


class TestInternalLinks:
    def test_internal_links_detected(self, good_blog_post):
        result = analyze_citations(good_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Internal Links')
        assert check['score'] > 0

    def test_no_internal_links(self, poor_blog_post):
        result = analyze_citations(poor_blog_post)
        check = next(c for c in result.checks if c['name'] == 'Internal Links')
        assert check['status'] == 'fail'

    def test_relative_links(self):
        text = 'See our [guide](/guide) and [FAQ](/faq) and [about](/about) pages.'
        result = analyze_citations(text)
        check = next(c for c in result.checks if c['name'] == 'Internal Links')
        assert check['score'] > 0


class TestOverall:
    def test_good_scores_higher(self, good_blog_post, poor_blog_post):
        good = analyze_citations(good_blog_post)
        poor = analyze_citations(poor_blog_post)
        assert good.percentage > poor.percentage

    def test_max_score(self):
        result = analyze_citations('')
        assert result.max_score == 50.0

    def test_category(self):
        result = analyze_citations('')
        assert result.category == 'citations'
