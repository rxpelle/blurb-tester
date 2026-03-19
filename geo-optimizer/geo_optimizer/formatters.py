"""Rich table + JSON output formatting."""

from __future__ import annotations

import json
from dataclasses import asdict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from geo_optimizer.models import AnalysisResult, GEOScore, Recommendation

console = Console()

STATUS_COLORS = {
    'pass': 'green',
    'warn': 'yellow',
    'fail': 'red',
}

STATUS_ICONS = {
    'pass': '[green]PASS[/green]',
    'warn': '[yellow]WARN[/yellow]',
    'fail': '[red]FAIL[/red]',
}

PRIORITY_COLORS = {
    'high': 'red',
    'medium': 'yellow',
    'low': 'dim',
}

GRADE_COLORS = {
    'A': 'green',
    'B': 'cyan',
    'C': 'yellow',
    'D': 'red',
    'F': 'red bold',
}


def format_score(geo_score: GEOScore, output: str = 'table') -> None:
    """Display just the score."""
    if output == 'json':
        console.print_json(json.dumps(asdict(geo_score)))
        return

    grade_color = GRADE_COLORS.get(geo_score.grade, 'white')
    console.print(Panel(
        f'[bold {grade_color}]{geo_score.overall_score:.0f}/100 ({geo_score.grade})[/bold {grade_color}]',
        title='GEO Score',
        border_style=grade_color,
    ))


def format_analysis(
    geo_score: GEOScore,
    results: dict[str, AnalysisResult],
    recommendations: list[Recommendation],
    output: str = 'table',
) -> None:
    """Display full analysis with checks and recommendations."""
    if output == 'json':
        data = {
            'score': asdict(geo_score),
            'results': {k: asdict(v) for k, v in results.items()},
            'recommendations': [asdict(r) for r in recommendations],
        }
        console.print_json(json.dumps(data))
        return

    # Score header
    format_score(geo_score, output)

    # Category breakdown
    cat_table = Table(title='Category Scores', show_header=True)
    cat_table.add_column('Category', style='bold')
    cat_table.add_column('Score', justify='right')
    cat_table.add_column('Weight', justify='right')

    weight_labels = {
        'content': '30%',
        'structured_data': '25%',
        'citations': '20%',
        'landing_page': '25%',
    }

    for name, score in geo_score.category_scores.items():
        color = 'green' if score >= 75 else ('yellow' if score >= 50 else 'red')
        cat_table.add_row(
            name.replace('_', ' ').title(),
            f'[{color}]{score:.0f}%[/{color}]',
            weight_labels.get(name, ''),
        )

    console.print(cat_table)

    # Detailed checks
    for cat_name, result in results.items():
        check_table = Table(title=f'{cat_name.replace("_", " ").title()} Checks')
        check_table.add_column('Check', style='bold', min_width=20)
        check_table.add_column('Status', justify='center', min_width=6)
        check_table.add_column('Score', justify='right', min_width=8)
        check_table.add_column('Detail')

        for check in result.checks:
            status_icon = STATUS_ICONS.get(check['status'], check['status'])
            score_str = f"{check.get('score', 0):.0f}/{check.get('max', 10):.0f}"
            check_table.add_row(
                check['name'],
                status_icon,
                score_str,
                check['detail'],
            )

        console.print(check_table)

    # Recommendations
    if recommendations:
        rec_table = Table(title='Recommendations (by impact)')
        rec_table.add_column('Priority', justify='center', min_width=8)
        rec_table.add_column('Category', min_width=12)
        rec_table.add_column('Fix', min_width=40)
        rec_table.add_column('Impact', justify='right', min_width=6)

        for rec in recommendations:
            p_color = PRIORITY_COLORS.get(rec.priority, 'white')
            rec_table.add_row(
                f'[{p_color}]{rec.priority.upper()}[/{p_color}]',
                rec.category.replace('_', ' ').title(),
                rec.fix,
                f'+{rec.impact:.0f}',
            )

        console.print(rec_table)


def format_comparison(
    score_a: GEOScore,
    score_b: GEOScore,
    results_a: dict[str, AnalysisResult],
    results_b: dict[str, AnalysisResult],
    label_a: str,
    label_b: str,
    output: str = 'table',
) -> None:
    """Side-by-side comparison of two analyses."""
    if output == 'json':
        data = {
            label_a: {
                'score': asdict(score_a),
                'results': {k: asdict(v) for k, v in results_a.items()},
            },
            label_b: {
                'score': asdict(score_b),
                'results': {k: asdict(v) for k, v in results_b.items()},
            },
        }
        console.print_json(json.dumps(data))
        return

    table = Table(title='GEO Score Comparison')
    table.add_column('Metric', style='bold')
    table.add_column(label_a, justify='right')
    table.add_column(label_b, justify='right')
    table.add_column('Diff', justify='right')

    # Overall
    diff = score_b.overall_score - score_a.overall_score
    diff_color = 'green' if diff > 0 else ('red' if diff < 0 else 'dim')
    diff_str = f'[{diff_color}]{diff:+.0f}[/{diff_color}]'
    table.add_row(
        'Overall Score',
        f'{score_a.overall_score:.0f} ({score_a.grade})',
        f'{score_b.overall_score:.0f} ({score_b.grade})',
        diff_str,
    )

    # Categories
    all_cats = set(list(score_a.category_scores.keys()) + list(score_b.category_scores.keys()))
    for cat in sorted(all_cats):
        a_val = score_a.category_scores.get(cat, 0)
        b_val = score_b.category_scores.get(cat, 0)
        cat_diff = b_val - a_val
        cat_diff_color = 'green' if cat_diff > 0 else ('red' if cat_diff < 0 else 'dim')
        table.add_row(
            cat.replace('_', ' ').title(),
            f'{a_val:.0f}%',
            f'{b_val:.0f}%',
            f'[{cat_diff_color}]{cat_diff:+.0f}[/{cat_diff_color}]',
        )

    console.print(table)
