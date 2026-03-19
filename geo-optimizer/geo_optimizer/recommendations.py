"""Generate actionable fix recommendations."""

from __future__ import annotations

from geo_optimizer.models import AnalysisResult, Recommendation


def generate_recommendations(results: dict[str, AnalysisResult]) -> list[Recommendation]:
    """Generate actionable recommendations sorted by impact."""
    recs: list[Recommendation] = []

    for category, result in results.items():
        for check in result.checks:
            if check['status'] in ('fail', 'warn'):
                impact = check.get('max', 10) - check.get('score', 0)
                priority = _classify_priority(impact, check['status'])
                fix = _generate_fix(category, check['name'], check['detail'])

                rec = Recommendation(
                    priority=priority,
                    category=category,
                    issue=check['detail'],
                    fix=fix,
                    impact=impact,
                )
                recs.append(rec)

    # Deduplicate by issue text
    seen = set()
    unique = []
    for r in recs:
        key = (r.category, r.issue)
        if key not in seen:
            seen.add(key)
            unique.append(r)

    # Sort: high > medium > low, then by impact descending
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    unique.sort(key=lambda r: (priority_order.get(r.priority, 2), -r.impact))

    return unique


def _classify_priority(impact: float, status: str) -> str:
    if status == 'fail' and impact >= 8:
        return 'high'
    elif status == 'fail' or impact >= 5:
        return 'medium'
    else:
        return 'low'


FIX_MAP = {
    ('content', 'Direct Answers'): 'Start each H2 section with a 15-80 word paragraph that directly answers the heading. Make the first sentence a clear, quotable statement.',
    ('content', 'Question Headings'): 'Rephrase at least 3 H2/H3 headings as questions: "What is X?", "How does Y work?", "Why does Z matter?"',
    ('content', 'Paragraph Length'): 'Break long paragraphs into 40-80 word chunks. Each paragraph should convey one key idea that AI can extract as a snippet.',
    ('content', 'Key Takeaways'): 'Add a "## Key Takeaways" or "## TL;DR" section with 3-5 bullet points summarizing the main points.',
    ('content', 'Scannable Structure'): 'Add more H2/H3 headings so there is roughly 1 heading for every 3-5 paragraphs.',
    ('content', 'Lists & Tables'): 'Convert comparison text into tables. Add bulleted or numbered lists for steps, features, or options.',
    ('structured_data', 'JSON-LD Presence'): 'Add a <script type="application/ld+json"> block with Article or BlogPosting schema.',
    ('structured_data', 'Schema Types'): 'Add relevant Schema.org types: Article for blog posts, Book for book pages, FAQPage for Q&A content.',
    ('structured_data', 'Required Fields'): 'Complete all required schema fields: headline, author (as Person object), datePublished for articles; name, author, isbn for books.',
    ('structured_data', 'Author Markup'): 'Change the author field from a plain string to a Person object: {"@type": "Person", "name": "...", "url": "..."}',
    ('structured_data', 'Breadcrumb Markup'): 'Add BreadcrumbList schema to help AI engines understand your site navigation.',
    ('citations', 'External Links'): 'Add 3-5 links to authoritative external sources (.edu, .gov, major publications).',
    ('citations', 'Source Attribution'): 'Add "according to" or "research by" phrases to attribute claims to named sources.',
    ('citations', 'Data Citations'): 'Include specific statistics, years, and institutional references to support claims.',
    ('citations', 'Internal Links'): 'Add links to 3+ related pages on your own site.',
    ('citations', 'Link Quality'): 'Replace low-authority links with .edu, .gov, or major publication sources.',
    ('landing_page', 'Book Metadata'): 'Add missing book metadata: title, author, genre, page count, ISBN, price, and publication date.',
    ('landing_page', 'Comparison Positioning'): 'Add comp phrases: "Fans of [Author X] will love..." or "In the tradition of [Book Y]".',
    ('landing_page', 'Review Markup'): 'Add reader reviews/testimonials with Review schema markup.',
    ('landing_page', 'Buy Links'): 'Add prominent buy links to Amazon, Barnes & Noble, and other retailers.',
    ('landing_page', 'Series Information'): 'Clearly state the book\'s position: "Book 2 in the [Series Name] series".',
    ('landing_page', 'Author Bio'): 'Add an "About the Author" section with credentials and links.',
}


def _generate_fix(category: str, check_name: str, detail: str) -> str:
    """Generate a specific fix recommendation."""
    return FIX_MAP.get((category, check_name), f'Address: {detail}')
