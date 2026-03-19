"""Tests for recommendation generation."""

import pytest
from geo_optimizer.models import AnalysisResult
from geo_optimizer.recommendations import generate_recommendations


class TestRecommendationGeneration:
    def test_generates_recommendations_for_failures(self):
        results = {
            'content': AnalysisResult(
                category='content', score=0, max_score=60,
                checks=[
                    {'name': 'Direct Answers', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'No direct answers'},
                    {'name': 'Question Headings', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'No questions'},
                ],
            ),
        }
        recs = generate_recommendations(results)
        assert len(recs) >= 2
        assert all(r.category == 'content' for r in recs)

    def test_no_recommendations_for_passing(self):
        results = {
            'content': AnalysisResult(
                category='content', score=60, max_score=60,
                checks=[
                    {'name': 'Direct Answers', 'status': 'pass', 'score': 10, 'max': 10, 'detail': 'Good'},
                ],
            ),
        }
        recs = generate_recommendations(results)
        assert len(recs) == 0

    def test_warns_generate_recommendations(self):
        results = {
            'content': AnalysisResult(
                category='content', score=5, max_score=60,
                checks=[
                    {'name': 'Key Takeaways', 'status': 'warn', 'score': 5, 'max': 10, 'detail': 'Bullets but no section'},
                ],
            ),
        }
        recs = generate_recommendations(results)
        assert len(recs) == 1


class TestPrioritySorting:
    def test_high_priority_first(self):
        results = {
            'content': AnalysisResult(
                category='content', score=0, max_score=60,
                checks=[
                    {'name': 'Lists & Tables', 'status': 'warn', 'score': 5, 'max': 10, 'detail': 'Low impact'},
                    {'name': 'Direct Answers', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'High impact'},
                ],
            ),
        }
        recs = generate_recommendations(results)
        assert recs[0].priority in ('high', 'medium')
        assert recs[0].impact >= recs[-1].impact

    def test_multiple_categories_sorted(self):
        results = {
            'content': AnalysisResult(
                category='content', score=0, max_score=60,
                checks=[
                    {'name': 'Question Headings', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'No questions'},
                ],
            ),
            'citations': AnalysisResult(
                category='citations', score=0, max_score=50,
                checks=[
                    {'name': 'External Links', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'No links'},
                ],
            ),
        }
        recs = generate_recommendations(results)
        assert len(recs) == 2
        # Both should be high/medium priority
        assert all(r.priority in ('high', 'medium') for r in recs)


class TestDeduplication:
    def test_duplicate_issues_removed(self):
        results = {
            'content': AnalysisResult(
                category='content', score=0, max_score=60,
                checks=[
                    {'name': 'Check A', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'Same issue'},
                    {'name': 'Check A', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'Same issue'},
                ],
            ),
        }
        recs = generate_recommendations(results)
        # Should deduplicate
        issues = [(r.category, r.issue) for r in recs]
        assert len(issues) == len(set(issues))


class TestFixGeneration:
    def test_known_fix_returned(self):
        results = {
            'content': AnalysisResult(
                category='content', score=0, max_score=60,
                checks=[
                    {'name': 'Key Takeaways', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'No takeaways'},
                ],
            ),
        }
        recs = generate_recommendations(results)
        assert len(recs) == 1
        assert 'TL;DR' in recs[0].fix or 'takeaway' in recs[0].fix.lower()

    def test_unknown_check_gets_fallback(self):
        results = {
            'content': AnalysisResult(
                category='content', score=0, max_score=60,
                checks=[
                    {'name': 'Unknown Check', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'Something went wrong'},
                ],
            ),
        }
        recs = generate_recommendations(results)
        assert len(recs) == 1
        assert 'Something went wrong' in recs[0].fix
