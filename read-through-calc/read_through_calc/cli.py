import signal
import sys
import click
from rich.console import Console
from read_through_calc import __version__
from read_through_calc.config import Config
from read_through_calc.db import ReadOnlyDB
from read_through_calc.formatters import OutputFormatter
from read_through_calc.calculator import (
    build_read_through_report,
    calculate_ltv_from_db,
    pricing_scenario_from_db,
)

console = Console()


def _handle_sigint(sig, frame):
    console.print('\n[dim]Interrupted.[/dim]')
    sys.exit(0)


signal.signal(signal.SIGINT, _handle_sigint)


def _get_db(ctx) -> ReadOnlyDB:
    db_path = Config.get_db_path(ctx.obj.get('db_path'))
    return ReadOnlyDB(db_path)


@click.group()
@click.version_option(version=__version__, prog_name='read-through-calc')
@click.option('--db', 'db_path', default=None, type=click.Path(),
              help='Database path (default: ~/.book-data/books.db)')
@click.option('--output', '-o', type=click.Choice(['table', 'json']), default='table',
              help='Output format')
@click.pass_context
def main(ctx, db_path, output):
    """Series read-through rates, lifetime reader value, and pricing scenarios."""
    Config.setup_logging()
    ctx.ensure_object(dict)
    ctx.obj['db_path'] = db_path
    ctx.obj['output'] = output


@main.command('report')
@click.option('--series', '-s', default=None, help='Filter to a specific series')
@click.option('--window', '-w', default=None, type=int,
              help=f'Read window in days (default: {Config.READ_WINDOW_DAYS})')
@click.pass_context
def report(ctx, series, window):
    """Full read-through analysis for all series (or one)."""
    read_window = window or Config.READ_WINDOW_DAYS
    db = _get_db(ctx)
    formatter = OutputFormatter(ctx.obj.get('output', 'table'))
    try:
        if series:
            series_names = [series]
        else:
            series_names = db.get_series_names()

        if not series_names:
            console.print('[yellow]No series found. Use "book-data" to set up series_name and series_position.[/yellow]')
            return

        for name in series_names:
            r = build_read_through_report(db, name, read_window)
            formatter.format_read_through(r)
            if len(series_names) > 1:
                console.print()
    finally:
        db.close()


@main.command('ltv')
@click.option('--series', '-s', default=None, help='Filter to a specific series')
@click.option('--kenp-rate', default=None, type=float,
              help=f'KENP page rate (default: {Config.KU_PAGE_RATE})')
@click.option('--window', '-w', default=None, type=int,
              help=f'Read window in days (default: {Config.READ_WINDOW_DAYS})')
@click.pass_context
def ltv(ctx, series, kenp_rate, window):
    """Lifetime reader value per series."""
    kr = kenp_rate or Config.KU_PAGE_RATE
    read_window = window or Config.READ_WINDOW_DAYS
    db = _get_db(ctx)
    formatter = OutputFormatter(ctx.obj.get('output', 'table'))
    try:
        if series:
            series_names = [series]
        else:
            series_names = db.get_series_names()

        if not series_names:
            console.print('[yellow]No series found. Use "book-data" to set up series_name and series_position.[/yellow]')
            return

        for name in series_names:
            r = calculate_ltv_from_db(db, name, kr, read_window)
            formatter.format_ltv(r)
            if len(series_names) > 1:
                console.print()
    finally:
        db.close()


@main.command('pricing')
@click.option('--series', '-s', default=None, help='Filter to a specific series')
@click.option('--book1-price', type=float, default=None, help='Price for Book 1')
@click.option('--book2-price', type=float, default=None, help='Price for Book 2')
@click.option('--book3-price', type=float, default=None, help='Price for Book 3')
@click.option('--book4-price', type=float, default=None, help='Price for Book 4')
@click.option('--book5-price', type=float, default=None, help='Price for Book 5')
@click.option('--kenp-rate', default=None, type=float,
              help=f'KENP page rate (default: {Config.KU_PAGE_RATE})')
@click.option('--window', '-w', default=None, type=int,
              help=f'Read window in days (default: {Config.READ_WINDOW_DAYS})')
@click.pass_context
def pricing(ctx, series, book1_price, book2_price, book3_price,
            book4_price, book5_price, kenp_rate, window):
    """What-if pricing scenarios."""
    kr = kenp_rate or Config.KU_PAGE_RATE
    read_window = window or Config.READ_WINDOW_DAYS

    # Build price list from provided flags
    price_flags = [book1_price, book2_price, book3_price, book4_price, book5_price]
    prices = []
    for p in price_flags:
        if p is not None:
            prices.append(p)
        else:
            break  # Stop at first None

    if not prices:
        console.print('[yellow]Provide at least --book1-price to run a scenario.[/yellow]')
        return

    db = _get_db(ctx)
    formatter = OutputFormatter(ctx.obj.get('output', 'table'))
    try:
        if series:
            series_names = [series]
        else:
            series_names = db.get_series_names()

        if not series_names:
            console.print('[yellow]No series found. Use "book-data" to set up series_name and series_position.[/yellow]')
            return

        for name in series_names:
            r = pricing_scenario_from_db(db, name, prices, kr, read_window)
            formatter.format_pricing(r)
            if len(series_names) > 1:
                console.print()
    finally:
        db.close()


@main.command('config')
def show_config():
    """Show current configuration."""
    for key, value in Config.as_dict().items():
        console.print(f'  [cyan]{key}[/cyan]: {value}')
