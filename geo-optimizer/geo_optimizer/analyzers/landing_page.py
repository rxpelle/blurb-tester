"""Book landing page specific checks for GEO (25% of total score)."""

from __future__ import annotations

import re
from geo_optimizer.models import AnalysisResult


def analyze_landing_page(text: str, html: str | None = None, is_book_page: bool = False) -> AnalysisResult:
    """Analyze book landing page specific GEO signals."""
    result = AnalysisResult(category='landing_page', max_score=50.0)

    if not is_book_page:
        # Auto-detect: look for book-related signals
        content = html or text
        book_signals = re.findall(
            r'\b(?:ISBN|ASIN|pages?|hardcover|paperback|ebook|kindle|'
            r'buy now|add to cart|order now|available on amazon|'
            r'book (?:one|two|three|1|2|3)|series|novel|author)\b',
            content, re.IGNORECASE,
        )
        is_book_page = len(book_signals) >= 3

    if not is_book_page:
        # Return neutral score for non-book pages
        result.score = result.max_score * 0.6  # neutral
        result.checks.append({
            'name': 'Book Page Detection',
            'score': result.score, 'max': result.max_score,
            'status': 'pass',
            'detail': 'Not a book page. Landing page checks skipped (neutral score)',
        })
        return result

    _check_book_metadata(text, html, result)
    _check_comparison_positioning(text, result)
    _check_review_markup(text, html, result)
    _check_buy_links(text, html, result)
    _check_series_info(text, html, result)
    _check_author_bio(text, html, result)

    return result


BOOK_METADATA_FIELDS = {
    'title': [r'<h1[^>]*>(.+?)</h1>', r'^#\s+(.+)', r'"name"\s*:\s*"'],
    'author': [r'(?:by|author)\s*:?\s*([A-Z][a-z]+ [A-Z][a-z]+)', r'"author"'],
    'genre': [r'\b(?:genre|category)\s*:?\s*\w+', r'\b(?:thriller|mystery|romance|sci-fi|fantasy|horror|literary fiction|historical fiction)\b'],
    'pages': [r'\b(\d{2,4})\s*pages?\b', r'"numberOfPages"'],
    'isbn': [r'\bISBN[:\s-]*(\d[\d-]{9,})', r'"isbn"'],
    'price': [r'\$\d+\.?\d*', r'"price"'],
    'pub_date': [r'(?:published|publication|release)\s*(?:date)?\s*:?\s*\w+\s+\d{1,2},?\s+\d{4}', r'"datePublished"'],
}


def _check_book_metadata(text: str, html: str | None, result: AnalysisResult) -> None:
    """Book metadata completeness."""
    max_pts = 10.0
    content = html or text

    found = 0
    missing = []
    for field_name, patterns in BOOK_METADATA_FIELDS.items():
        field_found = False
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                field_found = True
                break
        if field_found:
            found += 1
        else:
            missing.append(field_name)

    total = len(BOOK_METADATA_FIELDS)
    ratio = found / total

    if ratio >= 0.8:
        result.score += max_pts
        result.checks.append({
            'name': 'Book Metadata',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{found}/{total} metadata fields present',
        })
    elif ratio >= 0.5:
        pts = max_pts * ratio
        result.score += pts
        result.checks.append({
            'name': 'Book Metadata',
            'score': pts, 'max': max_pts,
            'status': 'warn',
            'detail': f'{found}/{total} fields. Missing: {", ".join(missing)}',
        })
    else:
        result.checks.append({
            'name': 'Book Metadata',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': f'Only {found}/{total} fields. Missing: {", ".join(missing)}',
        })


def _check_comparison_positioning(text: str, result: AnalysisResult) -> None:
    """Does the page compare to known books?"""
    max_pts = 8.0

    comp_patterns = re.findall(
        r'(?:fans of|if you (?:liked?|enjoyed?|love)|readers of|'
        r'in the (?:vein|tradition|style) of|compared to|'
        r'meets|cross(?:es)? between|reminiscent of|'
        r'for (?:lovers|fans) of|perfect for fans)',
        text, re.IGNORECASE,
    )

    if comp_patterns:
        result.score += max_pts
        result.checks.append({
            'name': 'Comparison Positioning',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{len(comp_patterns)} comparison phrase(s) found ("fans of X" style)',
        })
    else:
        result.checks.append({
            'name': 'Comparison Positioning',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No comparison positioning. Add "Fans of X will love..." or "In the tradition of Y"',
        })


def _check_review_markup(text: str, html: str | None, result: AnalysisResult) -> None:
    """Are reviews present and structured?"""
    max_pts = 10.0
    content = html or text

    # Check for review patterns
    review_patterns = re.findall(
        r'(?:review|testimonial|praise|acclaim|"[^"]{20,}".*?[-\u2014]\s*\w+|'
        r'\u2605|\bstar(?:s)?\b.*?(?:rating|review)|rated\s+\d)',
        content, re.IGNORECASE,
    )

    # Check for structured review markup
    has_review_schema = bool(re.search(r'"@type"\s*:\s*"Review"', content))

    if has_review_schema and review_patterns:
        result.score += max_pts
        result.checks.append({
            'name': 'Review Markup',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': 'Reviews present with structured markup',
        })
    elif review_patterns:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Review Markup',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'{len(review_patterns)} review/testimonial patterns found but no Review schema',
        })
    else:
        result.checks.append({
            'name': 'Review Markup',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No reviews or testimonials. Add reader reviews with Review schema markup',
        })


def _check_buy_links(text: str, html: str | None, result: AnalysisResult) -> None:
    """Clear call-to-action with retailer links."""
    max_pts = 10.0
    content = html or text

    buy_patterns = re.findall(
        r'(?:buy now|order now|get (?:your|the|a) copy|add to cart|'
        r'available (?:now |on )|purchase|get it (?:on|at)|'
        r'amazon\.com|barnesandnoble\.com|bookshop\.org|'
        r'apple\.com/books|kobo\.com|'
        r'kindle|audible)',
        content, re.IGNORECASE,
    )

    if len(buy_patterns) >= 2:
        result.score += max_pts
        result.checks.append({
            'name': 'Buy Links',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{len(buy_patterns)} buy/CTA elements found',
        })
    elif len(buy_patterns) == 1:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Buy Links',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': '1 buy element. Add links to multiple retailers',
        })
    else:
        result.checks.append({
            'name': 'Buy Links',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No buy links or CTAs. Add prominent purchase links',
        })


def _check_series_info(text: str, html: str | None, result: AnalysisResult) -> None:
    """Is this book's position in a series clear?"""
    max_pts = 6.0
    content = html or text

    series_patterns = re.findall(
        r'(?:book\s+(?:one|two|three|four|five|\d+)|'
        r'(?:first|second|third|fourth|fifth)\s+(?:book|novel|installment)|'
        r'series|trilogy|duology|'
        r'volume\s+\d+|part\s+\d+|'
        r'#\d+\s+in\s+|'
        r'book\s+\d+\s+(?:of|in)\s+)',
        content, re.IGNORECASE,
    )

    if series_patterns:
        result.score += max_pts
        result.checks.append({
            'name': 'Series Information',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'Series positioning found ({len(series_patterns)} references)',
        })
    else:
        result.checks.append({
            'name': 'Series Information',
            'score': 0, 'max': max_pts,
            'status': 'warn',
            'detail': 'No series information found. If part of a series, make it explicit',
        })


def _check_author_bio(text: str, html: str | None, result: AnalysisResult) -> None:
    """Is there an author section with credentials?"""
    max_pts = 6.0
    content = html or text

    bio_patterns = re.findall(
        r'(?:about the author|author bio|written by|'
        r'<(?:section|div)[^>]*(?:author|bio)[^>]*>)',
        content, re.IGNORECASE,
    )

    if bio_patterns:
        result.score += max_pts
        result.checks.append({
            'name': 'Author Bio',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': 'Author bio section found',
        })
    else:
        result.checks.append({
            'name': 'Author Bio',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No author bio section. Add an "About the Author" section',
        })
