"""Schema.org / JSON-LD analysis for GEO (25% of total score)."""

from __future__ import annotations

import json
import re
from geo_optimizer.models import AnalysisResult


def analyze_structured_data(text: str, html: str | None = None) -> AnalysisResult:
    """Analyze Schema.org / JSON-LD structured data."""
    result = AnalysisResult(category='structured_data', max_score=50.0)

    is_html = html is not None
    content = html if is_html else text

    schemas = _extract_json_ld(content) if is_html else []

    _check_json_ld_presence(schemas, is_html, result)
    _check_schema_types(schemas, is_html, result)
    _check_required_fields(schemas, result)
    _check_author_markup(schemas, result)
    _check_breadcrumb(schemas, content, is_html, result)

    return result


def _extract_json_ld(html: str) -> list[dict]:
    """Extract JSON-LD blocks from HTML."""
    schemas = []
    pattern = re.compile(
        r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )
    for m in pattern.finditer(html):
        try:
            data = json.loads(m.group(1).strip())
            if isinstance(data, list):
                schemas.extend(data)
            else:
                schemas.append(data)
        except (json.JSONDecodeError, ValueError):
            schemas.append({'_invalid': True, '_raw': m.group(1).strip()})
    return schemas


def _check_json_ld_presence(schemas: list[dict], is_html: bool, result: AnalysisResult) -> None:
    """Does the page have JSON-LD?"""
    max_pts = 10.0

    if not is_html:
        result.checks.append({
            'name': 'JSON-LD Presence',
            'score': 0, 'max': max_pts,
            'status': 'warn',
            'detail': 'Markdown file. Ensure JSON-LD is added when publishing to HTML',
        })
        return

    valid = [s for s in schemas if not s.get('_invalid')]
    invalid = [s for s in schemas if s.get('_invalid')]

    if valid:
        result.score += max_pts
        result.checks.append({
            'name': 'JSON-LD Presence',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{len(valid)} valid JSON-LD block(s) found',
        })
    elif invalid:
        result.checks.append({
            'name': 'JSON-LD Presence',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': f'{len(invalid)} JSON-LD block(s) found but contain invalid JSON',
        })
    else:
        result.checks.append({
            'name': 'JSON-LD Presence',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No JSON-LD structured data found. Add <script type="application/ld+json">',
        })


RELEVANT_TYPES = {
    'Article', 'BlogPosting', 'NewsArticle', 'TechArticle',
    'Book', 'FAQPage', 'Person', 'WebPage', 'WebSite',
    'HowTo', 'Review', 'Product',
}


def _get_types(schemas: list[dict]) -> list[str]:
    """Get @type values from schemas, handling nested and list types."""
    types = []
    for s in schemas:
        if s.get('_invalid'):
            continue
        t = s.get('@type', '')
        if isinstance(t, list):
            types.extend(t)
        elif t:
            types.append(t)
    return types


def _check_schema_types(schemas: list[dict], is_html: bool, result: AnalysisResult) -> None:
    """Check for relevant Schema.org types."""
    max_pts = 10.0

    if not is_html:
        result.checks.append({
            'name': 'Schema Types',
            'score': 0, 'max': max_pts,
            'status': 'warn',
            'detail': 'Markdown file. Add Article or BlogPosting schema when published',
        })
        return

    types = _get_types(schemas)
    relevant = [t for t in types if t in RELEVANT_TYPES]

    if len(relevant) >= 2:
        result.score += max_pts
        result.checks.append({
            'name': 'Schema Types',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'Found types: {", ".join(relevant)}',
        })
    elif len(relevant) == 1:
        result.score += max_pts * 0.7
        result.checks.append({
            'name': 'Schema Types',
            'score': max_pts * 0.7, 'max': max_pts,
            'status': 'warn',
            'detail': f'Found: {relevant[0]}. Consider adding more types (FAQPage, BreadcrumbList)',
        })
    else:
        result.checks.append({
            'name': 'Schema Types',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No relevant Schema.org types found. Add Article, Book, or FAQPage markup',
        })


BOOK_REQUIRED = {'name', 'author', 'isbn', 'numberOfPages'}
ARTICLE_REQUIRED = {'headline', 'author', 'datePublished'}
FAQPAGE_REQUIRED = {'mainEntity'}


def _check_required_fields(schemas: list[dict], result: AnalysisResult) -> None:
    """Each schema type has required fields. Score based on completeness."""
    max_pts = 15.0

    valid = [s for s in schemas if not s.get('_invalid')]
    if not valid:
        result.checks.append({
            'name': 'Required Fields',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No schemas to validate',
        })
        return

    total_required = 0
    total_present = 0
    details = []

    for s in valid:
        schema_type = s.get('@type', '')
        if isinstance(schema_type, list):
            schema_type = schema_type[0] if schema_type else ''

        if schema_type == 'Book':
            req = BOOK_REQUIRED
        elif schema_type in ('Article', 'BlogPosting', 'NewsArticle', 'TechArticle'):
            req = ARTICLE_REQUIRED
        elif schema_type == 'FAQPage':
            req = FAQPAGE_REQUIRED
        else:
            continue

        present = {f for f in req if f in s and s[f]}
        missing = req - present
        total_required += len(req)
        total_present += len(present)

        if missing:
            details.append(f'{schema_type}: missing {", ".join(sorted(missing))}')

    if total_required == 0:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Required Fields',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': 'No Article/Book/FAQ schemas to validate fields against',
        })
        return

    ratio = total_present / total_required
    if ratio >= 0.9:
        result.score += max_pts
        result.checks.append({
            'name': 'Required Fields',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'Schema fields {total_present}/{total_required} complete',
        })
    elif ratio >= 0.5:
        pts = max_pts * ratio
        result.score += pts
        result.checks.append({
            'name': 'Required Fields',
            'score': pts, 'max': max_pts,
            'status': 'warn',
            'detail': f'{total_present}/{total_required} fields present. {"; ".join(details)}',
        })
    else:
        result.checks.append({
            'name': 'Required Fields',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': f'Only {total_present}/{total_required} fields. {"; ".join(details)}',
        })


def _check_author_markup(schemas: list[dict], result: AnalysisResult) -> None:
    """Is the author entity properly linked?"""
    max_pts = 10.0

    valid = [s for s in schemas if not s.get('_invalid')]
    if not valid:
        result.checks.append({
            'name': 'Author Markup',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No schemas found',
        })
        return

    has_author = False
    author_is_object = False
    for s in valid:
        author = s.get('author')
        if author:
            has_author = True
            if isinstance(author, dict) and author.get('@type'):
                author_is_object = True

    if author_is_object:
        result.score += max_pts
        result.checks.append({
            'name': 'Author Markup',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': 'Author is a structured Person/Organization entity',
        })
    elif has_author:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Author Markup',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': 'Author is a plain string. Use a Person object with @type, name, url',
        })
    else:
        result.checks.append({
            'name': 'Author Markup',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No author markup found in any schema',
        })


def _check_breadcrumb(schemas: list[dict], content: str, is_html: bool, result: AnalysisResult) -> None:
    """Does the page have BreadcrumbList?"""
    max_pts = 5.0

    if not is_html:
        result.checks.append({
            'name': 'Breadcrumb Markup',
            'score': 0, 'max': max_pts,
            'status': 'warn',
            'detail': 'Markdown file. Add BreadcrumbList schema when published',
        })
        return

    types = _get_types(schemas)
    if 'BreadcrumbList' in types:
        result.score += max_pts
        result.checks.append({
            'name': 'Breadcrumb Markup',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': 'BreadcrumbList schema found',
        })
    else:
        result.checks.append({
            'name': 'Breadcrumb Markup',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No BreadcrumbList markup. Add breadcrumb schema for better navigation signals',
        })
