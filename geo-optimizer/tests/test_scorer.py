"""Tests for the scoring engine."""

import pytest
from geo_optimizer.models import AnalysisResult
from geo_optimizer.scorer import calculate_geo_score, _assign_grade


class TestOverallScore:
    def test_perfect_scores(self):
        results = {
            'content': AnalysisResult(category='content', score=60, max_score=60),
            'structured_data': AnalysisResult(category='structured_data', score=50, max_score=50),
            'citations': AnalysisResult(category='citations', score=50, max_score=50),
            'landing_page': AnalysisResult(category='landing_page', score=50, max_score=50),
        }
        geo_score = calculate_geo_score(results, is_book_page=True)
        assert geo_score.overall_score == 100.0

    def test_zero_scores(self):
        results = {
            'content': AnalysisResult(category='content', score=0, max_score=60),
            'structured_data': AnalysisResult(category='structured_data', score=0, max_score=50),
            'citations': AnalysisResult(category='citations', score=0, max_score=50),
            'landing_page': AnalysisResult(category='landing_page', score=0, max_score=50),
        }
        geo_score = calculate_geo_score(results, is_book_page=True)
        assert geo_score.overall_score == 0.0

    def test_mixed_scores(self):
        results = {
            'content': AnalysisResult(category='content', score=30, max_score=60),  # 50%
            'structured_data': AnalysisResult(category='structured_data', score=25, max_score=50),  # 50%
            'citations': AnalysisResult(category='citations', score=25, max_score=50),  # 50%
            'landing_page': AnalysisResult(category='landing_page', score=25, max_score=50),  # 50%
        }
        geo_score = calculate_geo_score(results, is_book_page=True)
        assert geo_score.overall_score == 50.0

    def test_category_scores_populated(self):
        results = {
            'content': AnalysisResult(category='content', score=45, max_score=60),
            'structured_data': AnalysisResult(category='structured_data', score=40, max_score=50),
            'citations': AnalysisResult(category='citations', score=30, max_score=50),
            'landing_page': AnalysisResult(category='landing_page', score=35, max_score=50),
        }
        geo_score = calculate_geo_score(results, is_book_page=True)
        assert 'content' in geo_score.category_scores
        assert 'structured_data' in geo_score.category_scores
        assert 'citations' in geo_score.category_scores
        assert 'landing_page' in geo_score.category_scores


class TestGradeAssignment:
    def test_grade_a(self):
        assert _assign_grade(95) == 'A'
        assert _assign_grade(90) == 'A'

    def test_grade_b(self):
        assert _assign_grade(89) == 'B'
        assert _assign_grade(75) == 'B'

    def test_grade_c(self):
        assert _assign_grade(74) == 'C'
        assert _assign_grade(60) == 'C'

    def test_grade_d(self):
        assert _assign_grade(59) == 'D'
        assert _assign_grade(40) == 'D'

    def test_grade_f(self):
        assert _assign_grade(39) == 'F'
        assert _assign_grade(0) == 'F'

    def test_boundary_values(self):
        assert _assign_grade(90) == 'A'
        assert _assign_grade(89.9) == 'B'
        assert _assign_grade(75) == 'B'
        assert _assign_grade(74.9) == 'C'
        assert _assign_grade(60) == 'C'
        assert _assign_grade(59.9) == 'D'
        assert _assign_grade(40) == 'D'
        assert _assign_grade(39.9) == 'F'


class TestWeightRedistribution:
    def test_non_book_page_excludes_landing_page(self):
        results = {
            'content': AnalysisResult(category='content', score=60, max_score=60),
            'structured_data': AnalysisResult(category='structured_data', score=50, max_score=50),
            'citations': AnalysisResult(category='citations', score=50, max_score=50),
            'landing_page': AnalysisResult(category='landing_page', score=0, max_score=50),
        }
        # Non-book: landing_page weight redistributed, so zero landing_page doesn't hurt
        score_non_book = calculate_geo_score(results, is_book_page=False)
        score_book = calculate_geo_score(results, is_book_page=True)
        assert score_non_book.overall_score > score_book.overall_score


class TestTopIssues:
    def test_top_issues_extraction(self):
        results = {
            'content': AnalysisResult(
                category='content', score=0, max_score=60,
                checks=[
                    {'name': 'Test', 'status': 'fail', 'score': 0, 'max': 10, 'detail': 'Issue A'},
                    {'name': 'Test2', 'status': 'fail', 'score': 0, 'max': 5, 'detail': 'Issue B'},
                ],
            ),
            'structured_data': AnalysisResult(category='structured_data', score=50, max_score=50),
            'citations': AnalysisResult(category='citations', score=50, max_score=50),
            'landing_page': AnalysisResult(category='landing_page', score=50, max_score=50),
        }
        geo_score = calculate_geo_score(results)
        assert len(geo_score.top_issues) >= 1
        # Higher impact issue should come first
        assert 'Issue A' in geo_score.top_issues[0]

    def test_max_5_issues(self):
        checks = [
            {'name': f'Check{i}', 'status': 'fail', 'score': 0, 'max': 10, 'detail': f'Issue {i}'}
            for i in range(10)
        ]
        results = {
            'content': AnalysisResult(category='content', score=0, max_score=60, checks=checks),
            'structured_data': AnalysisResult(category='structured_data', score=50, max_score=50),
            'citations': AnalysisResult(category='citations', score=50, max_score=50),
            'landing_page': AnalysisResult(category='landing_page', score=50, max_score=50),
        }
        geo_score = calculate_geo_score(results)
        assert len(geo_score.top_issues) <= 5
