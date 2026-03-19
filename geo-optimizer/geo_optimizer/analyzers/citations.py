"""Citation and source quality analysis for GEO (20% of total score)."""

from __future__ import annotations

import re
from geo_optimizer.models import AnalysisResult


def analyze_citations(text: str, html: str | None = None) -> AnalysisResult:
    """Analyze citation quality for AI discoverability."""
    result = AnalysisResult(category='citations', max_score=50.0)

    content = html if html else text

    _check_external_links(text, html, result)
    _check_source_attribution(text, result)
    _check_data_citations(text, result)
    _check_internal_links(text, html, result)
    _check_link_quality(text, html, result)

    return result


def _extract_links(text: str, html: str | None = None) -> list[str]:
    """Extract all URLs from markdown or HTML."""
    urls = []
    # Markdown links: [text](url)
    urls.extend(re.findall(r'\[([^\]]*)\]\(([^)]+)\)', text))
    # Also get raw URLs
    urls_raw = re.findall(r'https?://[^\s<>")\]]+', html or text)
    all_urls = [u[1] if isinstance(u, tuple) else u for u in urls] + urls_raw
    return list(set(all_urls))


def _is_external_link(url: str) -> bool:
    """Check if a URL is external."""
    return url.startswith('http://') or url.startswith('https://')


def _check_external_links(text: str, html: str | None, result: AnalysisResult) -> None:
    """Pages with 3-5 authoritative external links score higher."""
    max_pts = 10.0

    links = _extract_links(text, html)
    external = [u for u in links if _is_external_link(u)]

    if 3 <= len(external) <= 8:
        result.score += max_pts
        result.checks.append({
            'name': 'External Links',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{len(external)} external links (ideal: 3-5)',
        })
    elif 1 <= len(external) <= 2:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'External Links',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'{len(external)} external link(s). Aim for 3-5 authoritative sources',
        })
    elif len(external) > 8:
        result.score += max_pts * 0.7
        result.checks.append({
            'name': 'External Links',
            'score': max_pts * 0.7, 'max': max_pts,
            'status': 'warn',
            'detail': f'{len(external)} external links. Consider trimming to most authoritative',
        })
    else:
        result.checks.append({
            'name': 'External Links',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No external links. Add 3-5 links to authoritative sources',
        })


def _check_source_attribution(text: str, result: AnalysisResult) -> None:
    """Are claims backed by named sources?"""
    max_pts = 10.0

    source_patterns = re.findall(
        r'(?:according to|research by|study by|reported by|published in|'
        r'data from|findings from|analysis by|survey by|per\s)',
        text, re.IGNORECASE,
    )

    # Named sources: proper nouns after attribution phrases
    named_sources = re.findall(
        r'(?:according to|by)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        text,
    )

    total = len(source_patterns) + len(named_sources)

    if total >= 3:
        result.score += max_pts
        result.checks.append({
            'name': 'Source Attribution',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{total} source attributions found',
        })
    elif total >= 1:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Source Attribution',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'{total} source attribution(s). Add more "according to X" references',
        })
    else:
        result.checks.append({
            'name': 'Source Attribution',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No source attributions. Back claims with "according to X", "research by Y"',
        })


def _check_data_citations(text: str, result: AnalysisResult) -> None:
    """Are statistics attributed?"""
    max_pts = 10.0

    # Statistics patterns: numbers with context
    stats = re.findall(
        r'\b\d+(?:\.\d+)?(?:\s*%|\s*percent|\s*million|\s*billion|\s*thousand)\b',
        text, re.IGNORECASE,
    )

    # Years with context
    years = re.findall(r'\b(1[89]\d{2}|20[0-3]\d)\b', text)

    # Named institutions
    institutions = re.findall(
        r'\b(?:Nature|Science|The Lancet|New England Journal|JAMA|WHO|CDC|NIH|FDA|'
        r'Harvard|MIT|Stanford|Oxford|Cambridge|Pew Research|Gallup|Reuters|'
        r'Bloomberg|McKinsey|Gartner)\b',
        text, re.IGNORECASE,
    )

    total = len(stats) + len(years) + len(institutions)

    if total >= 5:
        result.score += max_pts
        result.checks.append({
            'name': 'Data Citations',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{total} data points (stats: {len(stats)}, years: {len(years)}, institutions: {len(institutions)})',
        })
    elif total >= 2:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Data Citations',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'{total} data points. Add more specific numbers, dates, and named sources',
        })
    else:
        result.checks.append({
            'name': 'Data Citations',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'Few data points. Add statistics, years, and institutional references',
        })


def _check_internal_links(text: str, html: str | None, result: AnalysisResult) -> None:
    """Cross-links to related content help AI understand context."""
    max_pts = 10.0

    # Markdown relative links
    md_internal = re.findall(r'\[([^\]]*)\]\((?!/|https?://)([^)]+)\)', text)
    # Markdown links starting with /
    md_slash = re.findall(r'\[([^\]]*)\]\((/[^)]+)\)', text)
    # HTML relative links (if HTML provided)
    html_internal = []
    if html:
        html_internal = re.findall(r'href=["\'](?!/|https?://)([^"\']+)["\']', html)
        html_internal += re.findall(r'href=["\'](/[^"\']+)["\']', html)

    total = len(md_internal) + len(md_slash) + len(html_internal)

    if total >= 3:
        result.score += max_pts
        result.checks.append({
            'name': 'Internal Links',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{total} internal links found',
        })
    elif total >= 1:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Internal Links',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'{total} internal link(s). Add more cross-links to related content',
        })
    else:
        result.checks.append({
            'name': 'Internal Links',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No internal links. Link to related pages on your site',
        })


QUALITY_DOMAINS = {
    '.edu', '.gov', '.org',
    'nature.com', 'science.org', 'thelancet.com', 'nejm.org',
    'who.int', 'cdc.gov', 'nih.gov', 'fda.gov',
    'nytimes.com', 'washingtonpost.com', 'reuters.com', 'bbc.com',
    'harvard.edu', 'mit.edu', 'stanford.edu', 'oxford.ac.uk',
    'wikipedia.org', 'scholar.google.com',
}


def _check_link_quality(text: str, html: str | None, result: AnalysisResult) -> None:
    """Links to .edu, .gov, major publications score higher."""
    max_pts = 10.0

    links = _extract_links(text, html)
    external = [u for u in links if _is_external_link(u)]

    if not external:
        result.checks.append({
            'name': 'Link Quality',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No external links to evaluate quality',
        })
        return

    high_quality = 0
    for url in external:
        url_lower = url.lower()
        for domain in QUALITY_DOMAINS:
            if domain in url_lower:
                high_quality += 1
                break

    ratio = high_quality / len(external) if external else 0

    if ratio >= 0.5:
        result.score += max_pts
        result.checks.append({
            'name': 'Link Quality',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{high_quality}/{len(external)} links to high-authority domains',
        })
    elif high_quality >= 1:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Link Quality',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'{high_quality}/{len(external)} high-authority links. Add more .edu, .gov sources',
        })
    else:
        result.checks.append({
            'name': 'Link Quality',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No links to high-authority domains (.edu, .gov, major publications)',
        })
