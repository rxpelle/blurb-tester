import signal
import sys
import click
from rich.console import Console
from royalty_reconciler import __version__
from royalty_reconciler.config import Config
from royalty_reconciler.db import Database
from royalty_reconciler.formatters import OutputFormatter
from royalty_reconciler.parsers import parse_file, detect_platform, ParseError, SUPPORTED_PLATFORMS

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
@click.version_option(version=__version__, prog_name='royalty-reconciler')
@click.option('--db', 'db_path', default=None, type=click.Path(),
              help='Database path (default: ~/.book-data/books.db)')
@click.option('--output', '-o', type=click.Choice(['table', 'json']), default='table',
              help='Output format')
@click.pass_context
def main(ctx, db_path, output):
    """Royalty reconciler — ingest CSVs, normalize currencies, generate P&L and tax reports."""
    Config.setup_logging()
    ctx.ensure_object(dict)
    ctx.obj['db_path'] = db_path
    ctx.obj['output'] = output


@main.command('import')
@click.argument('file', type=click.Path(exists=True))
@click.option('--platform', '-p', type=click.Choice(SUPPORTED_PLATFORMS),
              default=None, help='Platform (auto-detected if omitted)')
@click.option('--asin', '-a', default=None, help='ASIN to associate records with')
@click.pass_context
def import_csv(ctx, file, platform, asin):
    """Import a royalty CSV from a publishing platform."""
    db = _get_db(ctx)
    formatter = _get_formatter(ctx)
    try:
        # Auto-detect platform if not specified
        if not platform:
            platform = detect_platform(file)
            if platform == 'unknown':
                console.print('[red]Could not auto-detect platform. Use --platform flag.[/red]')
                return
            console.print(f'[dim]Auto-detected platform: {platform}[/dim]')

        # Resolve book_id from ASIN
        book_id = None
        if asin:
            book = db.get_book_by_asin(asin)
            if not book:
                console.print(f'[red]No book found with ASIN {asin}. '
                            f'Add it with book-data first.[/red]')
                return
            book_id = book['id']

        # Parse the file
        try:
            records = parse_file(file, platform, book_id)
        except ParseError as e:
            console.print(f'[red]Parse error: {e}[/red]')
            return

        if not records:
            console.print('[yellow]No records found in CSV.[/yellow]')
            return

        # Import into database
        count = db.add_sales_bulk(records)
        formatter.format_import_result(count, platform, file)
    finally:
        db.close()


@main.command('pnl')
@click.option('--month', '-m', default=None, help='Month (YYYY-MM)')
@click.option('--year', '-y', default=None, type=int, help='Year (YYYY)')
@click.pass_context
def pnl(ctx, month, year):
    """Generate a profit & loss report."""
    from royalty_reconciler.reconciler import build_pnl

    if not month and not year:
        console.print('[red]Specify --month YYYY-MM or --year YYYY[/red]')
        return

    db = _get_db(ctx)
    formatter = _get_formatter(ctx)
    try:
        if month:
            parts = month.split('-')
            if len(parts) != 2:
                console.print('[red]Month format must be YYYY-MM[/red]')
                return
            y, m = int(parts[0]), int(parts[1])
            sales = db.get_sales_by_month(y, m)
            expenses = db.get_expenses(year=y, month=m)
            period = month
        else:
            sales = db.get_sales_by_year(year)
            expenses = db.get_expenses(year=year)
            period = str(year)

        report = build_pnl(sales, expenses, period)
        formatter.format_pnl(report)
    finally:
        db.close()


@main.command('tax')
@click.option('--year', '-y', required=True, type=int, help='Tax year')
@click.option('--export', '-e', type=click.Path(), default=None,
              help='Export as CSV to file path')
@click.pass_context
def tax(ctx, year, export):
    """Generate a Schedule C tax report."""
    from royalty_reconciler.tax import generate_tax_report, export_tax_csv

    db = _get_db(ctx)
    formatter = _get_formatter(ctx)
    try:
        sales = db.get_sales_by_year(year)
        expenses = db.get_expenses(year=year)

        report = generate_tax_report(sales, expenses, year)
        formatter.format_tax_report(report)

        if export:
            csv_content = export_tax_csv(report)
            with open(export, 'w') as f:
                f.write(csv_content)
            console.print(f'[green]Exported to {export}[/green]')
    finally:
        db.close()


@main.command('add-expense')
@click.option('--amount', '-a', required=True, type=float, help='Expense amount')
@click.option('--category', '-c', required=True,
              help='Category: ads, editing, cover, formatting, tools, software, etc.')
@click.option('--date', '-d', required=True, help='Date (YYYY-MM-DD)')
@click.option('--description', default='', help='Description of expense')
@click.option('--book-asin', default=None, help='ASIN of associated book')
@click.option('--currency', default='USD', help='Currency (default: USD)')
@click.pass_context
def add_expense(ctx, amount, category, date, description, book_asin, currency):
    """Track a business expense."""
    db = _get_db(ctx)
    formatter = _get_formatter(ctx)
    try:
        book_id = None
        if book_asin:
            book = db.get_book_by_asin(book_asin)
            if book:
                book_id = book['id']

        expense_id = db.add_expense(
            date=date, amount=amount, category=category,
            book_id=book_id, currency=currency,
            description=description,
        )
        formatter.format_expense_added(expense_id, amount, category, date)
    finally:
        db.close()


@main.command('reconcile')
@click.option('--month', '-m', required=True, help='Month (YYYY-MM)')
@click.pass_context
def reconcile(ctx, month):
    """Compare expected vs received payments for a month."""
    from royalty_reconciler.reconciler import reconcile_month

    parts = month.split('-')
    if len(parts) != 2:
        console.print('[red]Month format must be YYYY-MM[/red]')
        return

    db = _get_db(ctx)
    formatter = _get_formatter(ctx)
    try:
        y, m = int(parts[0]), int(parts[1])
        sales = db.get_sales_by_month(y, m)
        results = reconcile_month(sales, month)
        formatter.format_reconciliation(results)
    finally:
        db.close()


@main.command('status')
@click.pass_context
def status(ctx):
    """Show import history and last import dates per platform."""
    db = _get_db(ctx)
    formatter = _get_formatter(ctx)
    try:
        summaries = db.get_import_summary()
        formatter.format_status(summaries)
    finally:
        db.close()


@main.command('config')
def show_config():
    """Show current configuration."""
    for key, value in Config.as_dict().items():
        console.print(f'  [cyan]{key}[/cyan]: {value}')
