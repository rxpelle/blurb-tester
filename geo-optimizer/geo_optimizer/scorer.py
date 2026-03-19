"""Unified scoring engine - weighted aggregate."""

from __future__ import annotations

from geo_optimizer.config import Config
from geo_optimizer.models import AnalysisResult, GEOScore


def calculate_geo_score(results: dict[str, AnalysisResult], is_book_page: bool = False) -> GEOScore:
    """Calculate weighted GEO score from analyzer results.

    Weights:
    - Content structure: 30%
    - Structured data: 25%
    - Citations: 20%
    - Landing page: 25%

    For non-book pages, redistribute landing_page weight to other categories.
    """
    # Get category percentages (0-100 scale)
    category_scores = {}
    for name, r in results.items():
        category_scores[name] = r.percentage

    # Determine weights
    if is_book_page:
        weights = {
            'content': Config.WEIGHT_CONTENT,
            'structured_data': Config.WEIGHT_STRUCTURED_DATA,
            'citations': Config.WEIGHT_CITATIONS,
            'landing_page': Config.WEIGHT_LANDING_PAGE,
        }
    else:
        # Redistribute landing_page weight
        extra = Config.WEIGHT_LANDING_PAGE
        base_total = Config.WEIGHT_CONTENT + Config.WEIGHT_STRUCTURED_DATA + Config.WEIGHT_CITATIONS
        weights = {
            'content': Config.WEIGHT_CONTENT + extra * (Config.WEIGHT_CONTENT / base_total),
            'structured_data': Config.WEIGHT_STRUCTURED_DATA + extra * (Config.WEIGHT_STRUCTURED_DATA / base_total),
            'citations': Config.WEIGHT_CITATIONS + extra * (Config.WEIGHT_CITATIONS / base_total),
            'landing_page': 0.0,
        }

    # Calculate weighted score
    overall = 0.0
    for name, weight in weights.items():
        if name in category_scores and weight > 0:
            overall += category_scores[name] * weight

    overall = round(overall, 1)

    # Grade
    grade = _assign_grade(overall)

    # Top issues: collect failed checks sorted by max score (highest impact first)
    top_issues = _extract_top_issues(results)

    return GEOScore(
        overall_score=overall,
        category_scores=category_scores,
        grade=grade,
        top_issues=top_issues,
    )


def _assign_grade(score: float) -> str:
    if score >= 90:
        return 'A'
    elif score >= 75:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 40:
        return 'D'
    else:
        return 'F'


def _extract_top_issues(results: dict[str, AnalysisResult], max_issues: int = 5) -> list[str]:
    """Get highest-impact failed checks."""
    issues = []
    for name, r in results.items():
        for check in r.checks:
            if check['status'] in ('fail', 'warn'):
                impact = check.get('max', 10) - check.get('score', 0)
                issues.append((impact, f"[{name}] {check['detail']}"))

    issues.sort(key=lambda x: x[0], reverse=True)
    return [issue for _, issue in issues[:max_issues]]
