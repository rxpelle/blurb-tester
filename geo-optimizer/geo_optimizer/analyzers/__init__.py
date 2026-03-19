"""GEO analyzers package."""

from __future__ import annotations

from geo_optimizer.models import AnalysisResult
from geo_optimizer.analyzers.content import analyze_content
from geo_optimizer.analyzers.structured_data import analyze_structured_data
from geo_optimizer.analyzers.citations import analyze_citations
from geo_optimizer.analyzers.landing_page import analyze_landing_page


def run_all_analyzers(text: str, html: str | None = None, is_book_page: bool = False) -> dict[str, AnalysisResult]:
    """Run all analyzers and return results keyed by category name."""
    results = {}
    results['content'] = analyze_content(text)
    results['structured_data'] = analyze_structured_data(text, html)
    results['citations'] = analyze_citations(text, html)
    results['landing_page'] = analyze_landing_page(text, html, is_book_page)
    return results
