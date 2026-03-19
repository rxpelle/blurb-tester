"""Click CLI for GEO Optimizer."""

from __future__ import annotations

import signal
import sys

import click
import requests
from bs4 import BeautifulSoup
from rich.console import Console

from geo_optimizer import __version__
from geo_optimizer.analyzers import run_all_analyzers
from geo_optimizer.config import Config
from geo_optimizer.formatters import format_analysis, format_comparison, format_score
from geo_optimizer.recommendations import generate_recommendations
from geo_optimizer.scorer import calculate_geo_score

console = Console()


def _handle_sigint(sig, frame):
    console.print('\n[dim]Interrupted.[/dim]')
    sys.exit(0)


signal.signal(signal.SIGINT, _handle_sigint)


def _load_content(file: str | None, url: str | None) -> tuple[str, str | None, str]:
    """Load content from file or URL. Returns (text, html_or_none, label)."""
    if url:
        try:
            resp = requests.get(url, timeout=15, headers={
                'User-Agent': 'GEO-Optimizer/0.1.0',
            })
            resp.raise_for_status()
        except requests.RequestException as e:
            console.print(f'[red]Error fetching URL: {e}[/red]')
            sys.exit(1)

        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        return text, html, url

    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            console.print(f'[red]File not found: {file}[/red]')
            sys.exit(1)
        except OSError as e:
            console.print(f'[red]Error reading file: {e}[/red]')
            sys.exit(1)

        # Detect HTML
        if file.endswith(('.html', '.htm')) or content.strip().startswith(('<!DOCTYPE', '<html', '<HTML')):
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            return text, content, file
        else:
            return content, None, file

    console.print('[red]Provide either a file path or --url[/red]')
    sys.exit(1)


@click.group()
@click.version_option(version=__version__, prog_name='geo-optimizer')
@click.option('--output', '-o', type=click.Choice(['table', 'json']), default='table',
              help='Output format')
@click.pass_context
def main(ctx, output):
    """Optimize content for AI search engines (Generative Engine Optimization)."""
    Config.setup_logging()
    ctx.ensure_object(dict)
    ctx.obj['output'] = output


@main.command()
@click.argument('file', required=False, type=click.Path())
@click.option('--url', '-u', default=None, help='URL to fetch and analyze')
@click.pass_context
def analyze(ctx, file, url):
    """Full GEO analysis of a markdown or HTML file."""
    text, html, label = _load_content(file, url)
    output = ctx.obj.get('output', 'table')

    results = run_all_analyzers(text, html)
    is_book = results['landing_page'].checks and results['landing_page'].checks[0].get('name') != 'Book Page Detection'
    geo_score = calculate_geo_score(results, is_book)
    recs = generate_recommendations(results)

    if output != 'json':
        console.print(f'\n[bold]Analyzing:[/bold] {label}\n')

    format_analysis(geo_score, results, recs, output)


@main.command()
@click.argument('file', required=False, type=click.Path())
@click.option('--url', '-u', default=None, help='URL to fetch and score')
@click.pass_context
def score(ctx, file, url):
    """Just the numeric GEO score (0-100)."""
    text, html, label = _load_content(file, url)
    output = ctx.obj.get('output', 'table')

    results = run_all_analyzers(text, html)
    is_book = results['landing_page'].checks and results['landing_page'].checks[0].get('name') != 'Book Page Detection'
    geo_score = calculate_geo_score(results, is_book)

    if output != 'json':
        console.print(f'[dim]{label}[/dim]')

    format_score(geo_score, output)


@main.command()
@click.argument('file1', type=click.Path())
@click.argument('file2', type=click.Path())
@click.pass_context
def compare(ctx, file1, file2):
    """Side-by-side comparison of two pages."""
    output = ctx.obj.get('output', 'table')

    text_a, html_a, label_a = _load_content(file1, None)
    text_b, html_b, label_b = _load_content(file2, None)

    results_a = run_all_analyzers(text_a, html_a)
    results_b = run_all_analyzers(text_b, html_b)

    is_book_a = results_a['landing_page'].checks and results_a['landing_page'].checks[0].get('name') != 'Book Page Detection'
    is_book_b = results_b['landing_page'].checks and results_b['landing_page'].checks[0].get('name') != 'Book Page Detection'

    score_a = calculate_geo_score(results_a, is_book_a)
    score_b = calculate_geo_score(results_b, is_book_b)

    format_comparison(score_a, score_b, results_a, results_b, label_a, label_b, output)
