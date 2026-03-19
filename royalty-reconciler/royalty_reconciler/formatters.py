"""Rich table and JSON output formatters."""
import json
from typing import List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .models import PnLReport, TaxReport, ReconciliationResult

console = Console()


class OutputFormatter:
    def __init__(self, fmt: str = 'table'):
        self.fmt = fmt

    def format_import_result(self, count: int, platform: str, filepath: str):
        if self.fmt == 'json':
            console.print(json.dumps({
                'imported': count, 'platform': platform, 'file': filepath,
            }, indent=2))
            return
        console.print(f'[green]Imported {count} records from {platform}: {filepath}[/green]')

    def format_pnl(self, report: PnLReport):
        if self.fmt == 'json':
            console.print(json.dumps({
                'period': report.period,
                'gross_royalties': report.gross_royalties,
                'refunds': report.refunds,
                'net_royalties': report.net_royalties,
                'total_expenses': report.total_expenses,
                'net_profit': report.net_profit,
                'by_platform': report.by_platform,
                'by_book': {str(k): v for k, v in report.by_book.items()},
                'expense_breakdown': report.expense_breakdown,
            }, indent=2))
            return

        # Summary table
        table = Table(title=f'P&L Report: {report.period}')
        table.add_column('Item', style='bold')
        table.add_column('Amount', justify='right')

        color = 'green' if report.gross_royalties > 0 else 'dim'
        table.add_row('Gross Royalties', f'[{color}]${report.gross_royalties:.2f}[/{color}]')
        if report.refunds > 0:
            table.add_row('Refunds', f'[red]-${report.refunds:.2f}[/red]')
        table.add_row('Net Royalties', f'${report.net_royalties:.2f}')
        table.add_row('Total Expenses', f'[red]-${report.total_expenses:.2f}[/red]')

        profit_color = 'green' if report.net_profit >= 0 else 'red'
        table.add_row('Net Profit', f'[bold {profit_color}]${report.net_profit:.2f}[/bold {profit_color}]',
                      end_section=True)
        console.print(table)

        # Platform breakdown
        if report.by_platform:
            pt = Table(title='By Platform')
            pt.add_column('Platform', style='cyan')
            pt.add_column('Units', justify='right')
            pt.add_column('Royalties', justify='right', style='green')
            pt.add_column('Refunds', justify='right', style='red')
            for platform, data in sorted(report.by_platform.items()):
                pt.add_row(platform, str(data['units']),
                          f'${data["royalties"]:.2f}',
                          f'${data["refunds"]:.2f}')
            console.print(pt)

        # Expense breakdown
        if report.expense_breakdown:
            et = Table(title='Expenses by Category')
            et.add_column('Category', style='cyan')
            et.add_column('Amount', justify='right', style='red')
            for cat, amount in sorted(report.expense_breakdown.items(),
                                       key=lambda x: x[1], reverse=True):
                et.add_row(cat, f'${amount:.2f}')
            console.print(et)

    def format_tax_report(self, report: TaxReport):
        if self.fmt == 'json':
            console.print(json.dumps({
                'year': report.year,
                'gross_receipts': report.gross_receipts,
                'returns_allowances': report.returns_allowances,
                'advertising': report.advertising,
                'contract_labor': report.contract_labor,
                'office_expenses': report.office_expenses,
                'other_expenses': report.other_expenses,
                'total_expenses': report.total_expenses,
                'net_profit': report.net_profit,
                'platform_breakdown': report.platform_breakdown,
            }, indent=2))
            return

        table = Table(title=f'Schedule C Summary - Tax Year {report.year}')
        table.add_column('Line', width=6)
        table.add_column('Description', style='bold')
        table.add_column('Amount', justify='right')

        table.add_row('1', 'Gross receipts', f'${report.gross_receipts:.2f}')
        table.add_row('2', 'Returns and allowances', f'${report.returns_allowances:.2f}')
        net_receipts = report.gross_receipts - report.returns_allowances
        table.add_row('3', 'Net receipts', f'${net_receipts:.2f}', end_section=True)

        table.add_row('8', 'Advertising', f'${report.advertising:.2f}')
        table.add_row('11', 'Contract labor', f'${report.contract_labor:.2f}')
        table.add_row('18', 'Office expenses', f'${report.office_expenses:.2f}')
        table.add_row('27a', 'Other expenses', f'${report.other_expenses:.2f}')
        table.add_row('28', 'Total expenses', f'${report.total_expenses:.2f}', end_section=True)

        profit_color = 'green' if report.net_profit >= 0 else 'red'
        table.add_row('31', 'Net profit (or loss)',
                      f'[bold {profit_color}]${report.net_profit:.2f}[/bold {profit_color}]')

        console.print(table)

        if report.platform_breakdown:
            pt = Table(title='Income by Platform')
            pt.add_column('Platform', style='cyan')
            pt.add_column('Gross', justify='right', style='green')
            pt.add_column('Refunds', justify='right', style='red')
            pt.add_column('Net', justify='right', style='bold')
            for platform, data in sorted(report.platform_breakdown.items()):
                net = data['gross'] - data['refunds']
                pt.add_row(platform, f'${data["gross"]:.2f}',
                          f'${data["refunds"]:.2f}', f'${net:.2f}')
            console.print(pt)

    def format_reconciliation(self, results: List[ReconciliationResult]):
        if self.fmt == 'json':
            data = [{
                'platform': r.platform, 'month': r.month,
                'expected': r.expected_royalties,
                'received': r.received_payment,
                'discrepancy': r.discrepancy,
                'status': r.status, 'records': r.records,
            } for r in results]
            console.print(json.dumps(data, indent=2))
            return

        if not results:
            console.print('[dim]No records to reconcile.[/dim]')
            return

        month = results[0].month if results else ''
        table = Table(title=f'Payment Reconciliation: {month}')
        table.add_column('Platform', style='cyan')
        table.add_column('Records', justify='right')
        table.add_column('Expected', justify='right')
        table.add_column('Received', justify='right')
        table.add_column('Discrepancy', justify='right')
        table.add_column('Status')

        for r in results:
            status_style = {
                'matched': '[green]Matched[/green]',
                'pending': '[yellow]Pending[/yellow]',
                'underpaid': '[red]Underpaid[/red]',
                'overpaid': '[cyan]Overpaid[/cyan]',
            }.get(r.status, r.status)

            disc_color = 'green' if abs(r.discrepancy) < 0.01 else 'red'
            table.add_row(
                r.platform,
                str(r.records),
                f'${r.expected_royalties:.2f}',
                f'${r.received_payment:.2f}',
                f'[{disc_color}]${r.discrepancy:.2f}[/{disc_color}]',
                status_style,
            )

        console.print(table)

    def format_status(self, summaries: List[dict]):
        if self.fmt == 'json':
            console.print(json.dumps(summaries, indent=2))
            return

        if not summaries:
            console.print('[dim]No import data found.[/dim]')
            return

        table = Table(title='Import Status')
        table.add_column('Platform', style='cyan')
        table.add_column('Records', justify='right')
        table.add_column('Units', justify='right')
        table.add_column('Royalties', justify='right', style='green')
        table.add_column('Earliest', style='dim')
        table.add_column('Latest', style='dim')

        for s in summaries:
            table.add_row(
                s.get('platform', ''),
                str(s.get('record_count', 0)),
                str(s.get('total_units', 0)),
                f'${s.get("total_royalties", 0):.2f}',
                s.get('earliest_date', ''),
                s.get('latest_date', ''),
            )

        console.print(table)

    def format_expense_added(self, expense_id: int, amount: float,
                              category: str, date: str):
        if self.fmt == 'json':
            console.print(json.dumps({
                'id': expense_id, 'amount': amount,
                'category': category, 'date': date,
            }, indent=2))
            return
        console.print(
            f'[green]Added expense #{expense_id}: ${amount:.2f} ({category}) on {date}[/green]'
        )
