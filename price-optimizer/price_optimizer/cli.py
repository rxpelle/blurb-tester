import signal
import sys
import click
from rich.console import Console
from price_optimizer import __version__
from price_optimizer.config import Config
from price_optimizer.db import Database
from price_optimizer.formatters import OutputFormatter
from price_optimizer.royalty_calc import calculate_royalty
from price_optimizer.optimizer import analyze_price_elasticity, recommend_price
from price_optimizer.experiments import (
    start_experiment, get_experiments, update_experiment_status,
    cancel_experiment, get_experiment_schedule,
)

console = Console()


def _handle_sigint(sig, frame):
    console.print('\n[dim]Interrupted.[/dim]')
    sys.exit(0)


signal.signal(signal.SIGINT, _handle_sigint)


def _get_db(ctx) -> Database:
    return Database(Config.get_db_path(ctx.obj.get('db_path')))


def _get_formatter(ctx) -> OutputFormatter:
    return OutputFormatter(ctx.obj.get('output', 'table'))


@click.group()
@click.version_option(version=__version__, prog_name='price-optimizer')
@click.option('--db', 'db_path', default=None, type=click.Path(),
              help='Database path (default: ~/.book-data/books.db)')
@click.option('--output', '-o', type=click.Choice(['table', 'json']), default='table',
              help='Output format')
@click.pass_context
def main(ctx, db_path, output):
    """Price optimization for KDP books — track prices, analyze elasticity, maximize revenue."""
    Config.setup_logging()
    ctx.ensure_object(dict)
    ctx.obj['db_path'] = db_path
    ctx.obj['output'] = output


@main.command('log')
@click.option('--asin', '-a', required=True, help='Amazon ASIN')
@click.option('--price', '-p', required=True, type=float, help='New price')
@click.option('--old-price', type=float, default=None, help='Previous price')
@click.option('--format', 'book_format', default='ebook',
              type=click.Choice(['ebook', 'paperback', 'hardcover']),
              help='Book format')
@click.option('--marketplace', '-m', default='US', help='Marketplace code')
@click.option('--reason', '-r', default='', help='Reason for price change')
@click.option('--date', '-d', default=None, help='Date of change (YYYY-MM-DD)')
@click.pass_context
def log_price(ctx, asin, price, old_price, book_format, marketplace, reason, date):
    """Record a price change."""
    db = _get_db(ctx)
    try:
        book = db.get_book_by_asin(asin)
        if not book:
            console.print(f'[red]No book found with ASIN {asin}. Add it with book-data first.[/red]')
            return

        # If no old price provided, try to get it from the last price change
        if old_price is None:
            changes = db.get_price_changes(book.id)
            if changes:
                old_price = changes[-1].new_price

        pc_id = db.add_price_change(
            book_id=book.id,
            new_price=price,
            old_price=old_price,
            format=book_format,
            marketplace=marketplace,
            reason=reason,
            changed_at=date,
        )

        old_str = f'${old_price:.2f}' if old_price is not None else '?'
        console.print(
            f'[green]Logged price change #{pc_id} for {book.title}: '
            f'{old_str} -> ${price:.2f}'
            f'{f" ({reason})" if reason else ""}[/green]'
        )
    finally:
        db.close()


@main.command('history')
@click.option('--asin', '-a', required=True, help='Amazon ASIN')
@click.pass_context
def history(ctx, asin):
    """Show all price changes with BSR impact."""
    db = _get_db(ctx)
    try:
        book = db.get_book_by_asin(asin)
        if not book:
            console.print(f'[red]No book found with ASIN {asin}[/red]')
            return

        changes = db.get_price_changes(book.id)
        formatter = _get_formatter(ctx)
        formatter.format_price_history(book.title, book.asin, changes)
    finally:
        db.close()


@main.command('analyze')
@click.option('--asin', '-a', required=True, help='Amazon ASIN')
@click.pass_context
def analyze(ctx, asin):
    """Elasticity analysis: revenue/BSR at each price point."""
    db = _get_db(ctx)
    try:
        book = db.get_book_by_asin(asin)
        if not book:
            console.print(f'[red]No book found with ASIN {asin}[/red]')
            return

        changes = db.get_price_changes(book.id)
        sales = db.get_sales(book.id)
        snapshots = db.get_snapshots(book.id)

        price_points, elasticity = analyze_price_elasticity(changes, sales, snapshots)

        formatter = _get_formatter(ctx)
        formatter.format_analysis(book.title, book.asin, price_points, elasticity)
    finally:
        db.close()


@main.command('recommend')
@click.option('--asin', '-a', required=True, help='Amazon ASIN')
@click.pass_context
def recommend(ctx, asin):
    """Optimal price recommendation."""
    db = _get_db(ctx)
    try:
        book = db.get_book_by_asin(asin)
        if not book:
            console.print(f'[red]No book found with ASIN {asin}[/red]')
            return

        changes = db.get_price_changes(book.id)
        sales = db.get_sales(book.id)
        snapshots = db.get_snapshots(book.id)

        price_points, _ = analyze_price_elasticity(changes, sales, snapshots)
        rec = recommend_price(price_points, kenp_baseline=book.kenp_baseline)

        formatter = _get_formatter(ctx)
        formatter.format_recommendation(book.title, book.asin, rec)
    finally:
        db.close()


@main.command('royalty-calc')
@click.option('--price', '-p', required=True, type=float, help='List price')
@click.option('--format', 'book_format', default='ebook',
              type=click.Choice(['ebook', 'paperback', 'hardcover']),
              help='Book format')
@click.option('--marketplace', '-m', default='US', help='Marketplace code')
@click.option('--pages', type=int, default=None, help='Page count (for print cost estimation)')
@click.option('--print-cost', type=float, default=None, help='Explicit printing cost')
@click.option('--delivery-mb', type=float, default=0.5, help='eBook file size in MB')
@click.option('--color', is_flag=True, help='Color interior (affects print cost)')
@click.pass_context
def royalty_calc(ctx, price, book_format, marketplace, pages, print_cost, delivery_mb, color):
    """Show royalty at a given price point."""
    result = calculate_royalty(
        price=price,
        format=book_format,
        marketplace=marketplace,
        page_count=pages,
        print_cost=print_cost,
        delivery_mb=delivery_mb,
        color=color,
    )
    formatter = _get_formatter(ctx)
    formatter.format_royalty(result)


@main.group('experiment')
@click.pass_context
def experiment(ctx):
    """Manage price experiments."""
    pass


@experiment.command('start')
@click.option('--asin', '-a', required=True, help='Amazon ASIN')
@click.option('--prices', required=True, help='Comma-separated prices to test')
@click.option('--duration', '-d', default=14, type=int,
              help='Days per price point (default: 14)')
@click.pass_context
def experiment_start(ctx, asin, prices, duration):
    """Start a price experiment."""
    db = _get_db(ctx)
    try:
        book = db.get_book_by_asin(asin)
        if not book:
            console.print(f'[red]No book found with ASIN {asin}[/red]')
            return

        price_list = [float(p.strip()) for p in prices.split(',')]
        if len(price_list) < 2:
            console.print('[red]Need at least 2 prices to run an experiment.[/red]')
            return

        exp_path = Config.get_experiments_path()
        try:
            exp = start_experiment(exp_path, asin, price_list, duration)
            console.print(
                f'[green]Started experiment for {book.title}:[/green]\n'
                f'  Prices: {", ".join(f"${p:.2f}" for p in price_list)}\n'
                f'  Duration: {duration} days per price\n'
                f'  Total: {duration * len(price_list)} days\n'
                f'  Start now with: [bold]price-optimizer log -a {asin} -p {price_list[0]} -r "experiment"[/bold]'
            )
        except ValueError as e:
            console.print(f'[red]{e}[/red]')
    finally:
        db.close()


@experiment.command('status')
@click.option('--asin', '-a', default=None, help='Filter by ASIN')
@click.pass_context
def experiment_status(ctx, asin):
    """Check running experiments."""
    exp_path = Config.get_experiments_path()
    experiments = update_experiment_status(exp_path)

    if asin:
        experiments = [e for e in experiments if e.asin == asin]

    schedules = {}
    for exp in experiments:
        schedules[exp.asin] = get_experiment_schedule(exp)

    formatter = _get_formatter(ctx)
    formatter.format_experiments(experiments, schedules)


@experiment.command('results')
@click.option('--asin', '-a', required=True, help='Amazon ASIN')
@click.pass_context
def experiment_results(ctx, asin):
    """Analyze completed experiment results."""
    db = _get_db(ctx)
    try:
        book = db.get_book_by_asin(asin)
        if not book:
            console.print(f'[red]No book found with ASIN {asin}[/red]')
            return

        exp_path = Config.get_experiments_path()
        experiments = get_experiments(exp_path, asin=asin)

        if not experiments:
            console.print(f'[yellow]No experiments found for {asin}[/yellow]')
            return

        # Get the most recent experiment
        exp = experiments[-1]
        if exp.status == 'running':
            console.print('[yellow]Experiment still running. Results will be more accurate after completion.[/yellow]')

        # Run standard analysis using price change history
        changes = db.get_price_changes(book.id)
        sales = db.get_sales(book.id)
        snapshots = db.get_snapshots(book.id)

        price_points, elasticity = analyze_price_elasticity(changes, sales, snapshots)
        rec = recommend_price(price_points, kenp_baseline=book.kenp_baseline)

        formatter = _get_formatter(ctx)
        formatter.format_analysis(book.title, book.asin, price_points, elasticity)
        console.print()
        formatter.format_recommendation(book.title, book.asin, rec)
    finally:
        db.close()


@main.command('config')
def show_config():
    """Show current configuration."""
    for key, value in Config.as_dict().items():
        console.print(f'  [cyan]{key}[/cyan]: {value}')
