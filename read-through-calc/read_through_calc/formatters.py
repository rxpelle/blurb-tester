import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .models import ReadThroughReport, LTVReport, PricingScenario

console = Console()


class OutputFormatter:
    def __init__(self, format: str = 'table'):
        self.format = format

    def format_read_through(self, report: ReadThroughReport):
        if self.format == 'json':
            data = {
                'series': report.series_name,
                'books': [{'title': b.title, 'position': b.series_position} for b in report.books],
                'rates': [{
                    'from': r.from_book, 'to': r.to_book,
                    'from_units': r.from_units, 'to_units': r.to_units,
                    'overall_rate': round(r.overall_rate, 4),
                    'cohort_rate': round(r.cohort_rate, 4) if r.cohort_rate is not None else None,
                    'cohort_periods': r.cohort_periods,
                } for r in report.rates],
                'cumulative_rate': round(report.cumulative_rate, 4),
            }
            console.print(json.dumps(data, indent=2))
            return

        if not report.books:
            console.print(f'[dim]No books found for series "{report.series_name}"[/dim]')
            return

        if len(report.books) < 2:
            console.print(f'[yellow]Series "{report.series_name}" has only 1 book — no read-through to calculate.[/yellow]')
            return

        table = Table(title=f'Read-Through: {report.series_name}')
        table.add_column('From', style='bold')
        table.add_column('To', style='bold')
        table.add_column('Book 1 Units', justify='right')
        table.add_column('Book 2 Units', justify='right')
        table.add_column('Overall RT', justify='right', style='cyan')
        table.add_column('Cohort RT', justify='right', style='green')
        table.add_column('Periods', justify='right', style='dim')

        for r in report.rates:
            overall = f'{r.overall_rate:.1%}'
            cohort = f'{r.cohort_rate:.1%}' if r.cohort_rate is not None else '-'
            table.add_row(
                r.from_book, r.to_book,
                str(r.from_units), str(r.to_units),
                overall, cohort, str(r.cohort_periods),
            )

        console.print(table)
        console.print(f'\n  Cumulative read-through (Book 1 to last): [bold cyan]{report.cumulative_rate:.1%}[/bold cyan]')

    def format_ltv(self, report: LTVReport):
        if self.format == 'json':
            data = {
                'series': report.series_name,
                'books': [],
                'total_ltv': report.total_ltv,
                'kenp_rate': report.kenp_rate,
            }
            for i, book in enumerate(report.books):
                data['books'].append({
                    'title': book.title,
                    'position': book.series_position,
                    'avg_royalty': report.per_book_royalty[i],
                    'kenp_value': report.per_book_kenp_value[i],
                    'cumulative_rt': round(report.cumulative_rates[i], 4),
                    'ltv_contribution': report.per_book_ltv_contribution[i],
                })
            console.print(json.dumps(data, indent=2))
            return

        if not report.books:
            console.print('[dim]No books found.[/dim]')
            return

        table = Table(title=f'Lifetime Reader Value: {report.series_name}')
        table.add_column('#', style='dim', width=3)
        table.add_column('Title', style='bold')
        table.add_column('Avg Royalty', justify='right')
        table.add_column('KENP Value', justify='right')
        table.add_column('Cumulative RT', justify='right', style='cyan')
        table.add_column('LTV Contribution', justify='right', style='green')

        for i, book in enumerate(report.books):
            pos = str(book.series_position or i + 1)
            royalty = f'${report.per_book_royalty[i]:.2f}'
            kenp = f'${report.per_book_kenp_value[i]:.2f}'
            cum_rt = f'{report.cumulative_rates[i]:.1%}'
            ltv = f'${report.per_book_ltv_contribution[i]:.2f}'
            table.add_row(pos, book.title, royalty, kenp, cum_rt, ltv)

        console.print(table)
        console.print(f'\n  Total LTV per Book 1 reader: [bold green]${report.total_ltv:.2f}[/bold green]')
        console.print(f'  KENP page rate used: ${report.kenp_rate:.4f}')

    def format_pricing(self, scenario: PricingScenario):
        if self.format == 'json':
            data = {
                'series': scenario.series_name,
                'books': [],
                'total_ltv': scenario.total_ltv,
                'revenue_per_100_readers': scenario.revenue_per_100,
                'kenp_rate': scenario.kenp_rate,
            }
            for i, book in enumerate(scenario.books):
                data['books'].append({
                    'title': book.title,
                    'position': book.series_position,
                    'price': scenario.prices[i],
                    'royalty_rate': scenario.royalty_rates[i],
                    'per_unit_royalty': scenario.per_book_royalty[i],
                    'cumulative_rt': round(scenario.cumulative_rates[i], 4),
                    'ltv_contribution': scenario.per_book_ltv_contribution[i],
                })
            console.print(json.dumps(data, indent=2))
            return

        if not scenario.books:
            console.print('[dim]No books found.[/dim]')
            return

        table = Table(title=f'Pricing Scenario: {scenario.series_name}')
        table.add_column('#', style='dim', width=3)
        table.add_column('Title', style='bold')
        table.add_column('Price', justify='right')
        table.add_column('Royalty %', justify='right', style='dim')
        table.add_column('Per-Unit $', justify='right')
        table.add_column('Cumulative RT', justify='right', style='cyan')
        table.add_column('LTV Contribution', justify='right', style='green')

        for i, book in enumerate(scenario.books):
            pos = str(book.series_position or i + 1)
            price = f'${scenario.prices[i]:.2f}'
            rate = f'{scenario.royalty_rates[i]:.0%}'
            royalty = f'${scenario.per_book_royalty[i]:.2f}'
            cum_rt = f'{scenario.cumulative_rates[i]:.1%}'
            ltv = f'${scenario.per_book_ltv_contribution[i]:.2f}'
            table.add_row(pos, book.title, price, rate, royalty, cum_rt, ltv)

        console.print(table)
        console.print(f'\n  Total LTV per Book 1 reader: [bold green]${scenario.total_ltv:.2f}[/bold green]')
        console.print(f'  Revenue per 100 Book 1 readers: [bold green]${scenario.revenue_per_100:.2f}[/bold green]')
