"""Content structure analysis for GEO (30% of total score)."""

from __future__ import annotations

import re
from geo_optimizer.models import AnalysisResult


def analyze_content(text: str) -> AnalysisResult:
    """Analyze content structure for AI discoverability."""
    result = AnalysisResult(category='content', max_score=60.0)

    _check_direct_answers(text, result)
    _check_question_headings(text, result)
    _check_paragraph_length(text, result)
    _check_key_takeaways(text, result)
    _check_scannable_structure(text, result)
    _check_list_table_usage(text, result)

    return result


def _get_headings(text: str) -> list[tuple[int, str]]:
    """Extract headings as (level, text) tuples from markdown or HTML-stripped text."""
    headings = []
    for m in re.finditer(r'^(#{2,3})\s+(.+)', text, re.MULTILINE):
        level = len(m.group(1))
        headings.append((level, m.group(2).strip()))
    return headings


def _get_paragraphs(text: str) -> list[str]:
    """Extract non-heading, non-empty paragraph blocks."""
    paragraphs = []
    current = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == '':
            if current:
                paragraphs.append(' '.join(current))
                current = []
        elif re.match(r'^#{1,6}\s+', stripped):
            if current:
                paragraphs.append(' '.join(current))
                current = []
        elif re.match(r'^[-*]\s+', stripped) or re.match(r'^\d+\.\s+', stripped):
            if current:
                paragraphs.append(' '.join(current))
                current = []
        elif re.match(r'^\|', stripped):
            if current:
                paragraphs.append(' '.join(current))
                current = []
        else:
            current.append(stripped)
    if current:
        paragraphs.append(' '.join(current))
    return [p for p in paragraphs if len(p.split()) >= 3]


def _check_direct_answers(text: str, result: AnalysisResult) -> None:
    """First paragraph after each H2 should directly answer the heading's implied question."""
    result.max_score  # already set in aggregate
    max_pts = 10.0

    headings = re.finditer(r'^##\s+(.+)', text, re.MULTILINE)
    h2_list = list(headings)

    if not h2_list:
        result.checks.append({
            'name': 'Direct Answers',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No H2 headings found to check for direct answers',
        })
        return

    good_answers = 0
    for m in h2_list:
        # Get text after this heading until next heading or end
        start = m.end()
        next_heading = re.search(r'^#{1,3}\s+', text[start:], re.MULTILINE)
        section = text[start:start + next_heading.start()] if next_heading else text[start:]

        # Get first paragraph in this section
        lines = []
        started = False
        for line in section.splitlines():
            s = line.strip()
            if not started:
                if s == '' or s.startswith('#'):
                    continue
                started = True
            if started:
                if s == '':
                    break
                if s.startswith('#'):
                    break
                lines.append(s)

        if lines:
            first_para = ' '.join(lines)
            word_count = len(first_para.split())
            # Good direct answer: 15-80 words, starts with a declarative statement
            if 15 <= word_count <= 80:
                good_answers += 1

    ratio = good_answers / len(h2_list) if h2_list else 0
    if ratio >= 0.7:
        result.score += max_pts
        result.checks.append({
            'name': 'Direct Answers',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{good_answers}/{len(h2_list)} H2 sections have concise direct answers',
        })
    elif ratio >= 0.4:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Direct Answers',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'{good_answers}/{len(h2_list)} H2 sections have direct answers (aim for 70%+)',
        })
    else:
        result.checks.append({
            'name': 'Direct Answers',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': f'Only {good_answers}/{len(h2_list)} H2 sections have concise direct answers',
        })


def _check_question_headings(text: str, result: AnalysisResult) -> None:
    """H2/H3 headings phrased as questions."""
    max_pts = 10.0
    headings = _get_headings(text)
    question_headings = [h for _, h in headings if h.rstrip().endswith('?')]

    # Also check for implied questions: "How to", "What is", "Why", "When"
    implied = [h for _, h in headings if re.match(
        r'^(?:How|What|Why|When|Where|Who|Which|Is|Are|Can|Do|Does|Should|Will)\b',
        h, re.IGNORECASE
    ) and not h.rstrip().endswith('?')]

    total_question = len(question_headings) + len(implied)

    if total_question >= 3:
        result.score += max_pts
        result.checks.append({
            'name': 'Question Headings',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{total_question} question-format headings ({len(question_headings)} explicit, {len(implied)} implied)',
        })
    elif total_question >= 1:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Question Headings',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'{total_question} question heading(s) found (aim for 3+)',
        })
    else:
        result.checks.append({
            'name': 'Question Headings',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No question-format headings. Use headings like "What is X?" or "How to Y"',
        })


def _check_paragraph_length(text: str, result: AnalysisResult) -> None:
    """Paragraphs between 40-80 words are ideal for AI extraction."""
    max_pts = 10.0
    paragraphs = _get_paragraphs(text)

    if not paragraphs:
        result.checks.append({
            'name': 'Paragraph Length',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No paragraphs found',
        })
        return

    ideal_count = 0
    for p in paragraphs:
        wc = len(p.split())
        if 40 <= wc <= 80:
            ideal_count += 1

    ratio = ideal_count / len(paragraphs)
    avg_len = sum(len(p.split()) for p in paragraphs) / len(paragraphs)

    if ratio >= 0.5:
        result.score += max_pts
        result.checks.append({
            'name': 'Paragraph Length',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{ideal_count}/{len(paragraphs)} paragraphs in ideal 40-80 word range (avg: {avg_len:.0f})',
        })
    elif ratio >= 0.25:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Paragraph Length',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'{ideal_count}/{len(paragraphs)} paragraphs in ideal range (avg: {avg_len:.0f} words)',
        })
    else:
        result.checks.append({
            'name': 'Paragraph Length',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': f'Only {ideal_count}/{len(paragraphs)} paragraphs in 40-80 word range (avg: {avg_len:.0f})',
        })


def _check_key_takeaways(text: str, result: AnalysisResult) -> None:
    """Presence of summary boxes, TL;DR, key takeaways."""
    max_pts = 10.0

    takeaway_pattern = re.compile(
        r'^#{2,3}\s+(?:Key\s+Takeaways?|Quick\s+Facts?|Summary|TL;?\s*DR|'
        r'What\s+(?:You\s+(?:Need|Should)\s+Know|to\s+Remember)|'
        r'The\s+Bottom\s+Line|At\s+a\s+Glance|In\s+Brief)',
        re.MULTILINE | re.IGNORECASE,
    )
    has_section = bool(takeaway_pattern.search(text))

    bullet_runs = re.findall(r'(?:^[-*]\s+.+\n?){3,}', text, re.MULTILINE)

    if has_section:
        result.score += max_pts
        result.checks.append({
            'name': 'Key Takeaways',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': 'Key takeaways / summary section found',
        })
    elif bullet_runs:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Key Takeaways',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': 'Bullet lists found but no dedicated takeaways section heading',
        })
    else:
        result.checks.append({
            'name': 'Key Takeaways',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No key takeaways section. Add a bulleted summary for AI extraction',
        })


def _check_scannable_structure(text: str, result: AnalysisResult) -> None:
    """Ratio of headings to paragraphs. Good: 1 heading per 3-5 paragraphs."""
    max_pts = 10.0
    headings = _get_headings(text)
    paragraphs = _get_paragraphs(text)

    if not headings:
        result.checks.append({
            'name': 'Scannable Structure',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No headings found. Content needs structural headings',
        })
        return

    if not paragraphs:
        result.checks.append({
            'name': 'Scannable Structure',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No paragraphs found',
        })
        return

    ratio = len(paragraphs) / len(headings)
    if 2 <= ratio <= 6:
        result.score += max_pts
        result.checks.append({
            'name': 'Scannable Structure',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{len(headings)} headings, {len(paragraphs)} paragraphs (ratio: {ratio:.1f}, ideal: 3-5)',
        })
    elif 1 <= ratio <= 8:
        result.score += max_pts * 0.5
        result.checks.append({
            'name': 'Scannable Structure',
            'score': max_pts * 0.5, 'max': max_pts,
            'status': 'warn',
            'detail': f'Heading-to-paragraph ratio is {ratio:.1f} (ideal: 3-5)',
        })
    else:
        result.checks.append({
            'name': 'Scannable Structure',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': f'Heading-to-paragraph ratio is {ratio:.1f}. Add more headings to break up content',
        })


def _check_list_table_usage(text: str, result: AnalysisResult) -> None:
    """Structured data in lists and tables is more extractable than prose."""
    max_pts = 10.0

    # Count list items (bullet or numbered)
    list_items = re.findall(r'^[-*]\s+.+', text, re.MULTILINE)
    numbered_items = re.findall(r'^\d+\.\s+.+', text, re.MULTILINE)
    total_list = len(list_items) + len(numbered_items)

    # Count table rows
    table_rows = re.findall(r'^\|.+\|', text, re.MULTILINE)
    # Exclude separator rows
    table_rows = [r for r in table_rows if not re.match(r'^\|[\s\-:|]+\|$', r)]

    has_lists = total_list >= 3
    has_tables = len(table_rows) >= 2

    if has_lists and has_tables:
        result.score += max_pts
        result.checks.append({
            'name': 'Lists & Tables',
            'score': max_pts, 'max': max_pts,
            'status': 'pass',
            'detail': f'{total_list} list items and {len(table_rows)} table rows found',
        })
    elif has_lists or has_tables:
        result.score += max_pts * 0.7
        detail = f'{total_list} list items' if has_lists else f'{len(table_rows)} table rows'
        result.checks.append({
            'name': 'Lists & Tables',
            'score': max_pts * 0.7, 'max': max_pts,
            'status': 'warn',
            'detail': f'{detail} found. Consider adding {"tables" if has_lists else "lists"} too',
        })
    else:
        result.checks.append({
            'name': 'Lists & Tables',
            'score': 0, 'max': max_pts,
            'status': 'fail',
            'detail': 'No lists or tables found. Add structured data for better AI extraction',
        })
