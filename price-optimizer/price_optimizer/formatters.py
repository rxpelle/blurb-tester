"""Rich table and JSON output formatting."""

import json
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .models import PricePoint, ElasticityResult, Experiment, Recommendation, RoyaltyResult

console = Console()


class OutputFormatter:
    def __init__(self, format: str = 'table'):
        self.format = format

    def format_price_history(self, book_title, asin, price_changes):
        if self.format == 'json':
            data = {
                'book': {'title': book_title, 'asin': asin},
                'price_changes': [
                    {
                        'old_price': pc.old_price,
                        'new_price': pc.new_price,
                        'format': pc.format,
                        'marketplace': pc.marketplace,
                        'changed_at': pc.changed_at,
                        'reason': pc.reason,
                    }
                    for pc in price_changes
                ],
            }
            console.print(json.dumps(data, indent=2))
            return

        if not price_changes:
            console.print(f'[dim]No price changes recorded for {book_title} ({asin})[/dim]')
            return

        table = Table(title=f'Price History: {book_title} ({asin})')
        table.add_column('Date', style='dim')
        table.add_column('Old Price', justify='right')
        table.add_column('New Price', justify='right', style='bold')
        table.add_column('Format')
        table.add_column('Market')
        table.add_column('Reason')

        for pc in price_changes:
            old = f'${pc.old_price:.2f}' if pc.old_price is not None else '-'
            table.add_row(
                pc.changed_at, old, f'${pc.new_price:.2f}',
                pc.format, pc.marketplace, pc.reason,
            )

        console.print(table)

    def format_analysis(self, book_title, asin, price_points, elasticity_results):
        if self.format == 'json':
            data = {
                'book': {'title': book_title, 'asin': asin},
                'price_points': [
                    {
                        'price': pp.price,
                        'days_active': pp.days_active,
                        'total_units': pp.total_units,
                        'avg_daily_units': pp.avg_daily_units,
                        'avg_bsr': pp.avg_bsr,
                        'daily_revenue': pp.daily_revenue,
                        'royalty_per_unit': pp.royalty_per_unit,
                        'start_date': pp.start_date,
                        'end_date': pp.end_date,
                    }
                    for pp in price_points
                ],
                'elasticity': [
                    {
                        'price_from': er.price_from,
                        'price_to': er.price_to,
                        'pct_price_change': er.pct_price_change,
                        'pct_quantity_change': er.pct_quantity_change,
                        'elasticity': er.elasticity,
                        'interpretation': er.interpretation,
                    }
                    for er in elasticity_results
                ],
            }
            console.print(json.dumps(data, indent=2))
            return

        if not price_points:
            console.print(f'[dim]No price data to analyze for {book_title} ({asin})[/dim]')
            return

        # Price points table
        table = Table(title=f'Price Analysis: {book_title} ({asin})')
        table.add_column('Price', justify='right', style='bold')
        table.add_column('Days', justify='right')
        table.add_column('Units', justify='right')
        table.add_column('Avg/Day', justify='right')
        table.add_column('Avg BSR', justify='right')
        table.add_column('Royalty/Unit', justify='right', style='green')
        table.add_column('Rev/Day', justify='right', style='green bold')
        table.add_column('Period')

        for pp in price_points:
            bsr = f'{pp.avg_bsr:,.0f}' if pp.avg_bsr else '-'
            table.add_row(
                f'${pp.price:.2f}', str(pp.days_active),
                str(pp.total_units), f'{pp.avg_daily_units:.2f}',
                bsr, f'${pp.royalty_per_unit:.2f}',
                f'${pp.daily_revenue:.2f}',
                f'{pp.start_date} to {pp.end_date}',
            )

        console.print(table)

        # Elasticity table
        if elasticity_results:
            console.print()
            etable = Table(title='Price Elasticity')
            etable.add_column('From', justify='right')
            etable.add_column('To', justify='right')
            etable.add_column('Price Change', justify='right')
            etable.add_column('Qty Change', justify='right')
            etable.add_column('Elasticity', justify='right', style='bold')
            etable.add_column('Interpretation')

            for er in elasticity_results:
                etable.add_row(
                    f'${er.price_from:.2f}', f'${er.price_to:.2f}',
                    f'{er.pct_price_change:+.1f}%',
                    f'{er.pct_quantity_change:+.1f}%',
                    f'{er.elasticity:.2f}', er.interpretation,
                )

            console.print(etable)

    def format_recommendation(self, book_title, asin, rec):
        if self.format == 'json':
            data = {
                'book': {'title': book_title, 'asin': asin},
                'recommendation': {
                    'recommended_price': rec.recommended_price,
                    'estimated_daily_revenue': rec.estimated_daily_revenue,
                    'estimated_daily_units': rec.estimated_daily_units,
                    'estimated_royalty': rec.estimated_royalty,
                    'confidence': rec.confidence,
                    'reasoning': rec.reasoning,
                    'price_points_analyzed': rec.price_points_analyzed,
                },
            }
            console.print(json.dumps(data, indent=2))
            return

        if rec.recommended_price is None:
            console.print(f'[yellow]{rec.reasoning}[/yellow]')
            return

        confidence_style = {
            'high': 'green',
            'medium': 'yellow',
            'low': 'red',
        }.get(rec.confidence, 'dim')

        panel_text = (
            f'[bold]Recommended Price:[/bold] ${rec.recommended_price:.2f}\n'
            f'[bold]Est. Daily Revenue:[/bold] ${rec.estimated_daily_revenue:.2f}\n'
            f'[bold]Est. Daily Units:[/bold] {rec.estimated_daily_units:.1f}\n'
            f'[bold]Royalty Per Unit:[/bold] ${rec.estimated_royalty:.2f}\n'
            f'[bold]Confidence:[/bold] [{confidence_style}]{rec.confidence}[/{confidence_style}]\n'
            f'\n{rec.reasoning}'
        )

        console.print(Panel(panel_text,
                           title=f'Price Recommendation: {book_title}',
                           border_style='cyan'))

    def format_royalty(self, result):
        if self.format == 'json':
            data = {
                'price': result.price,
                'format': result.format,
                'marketplace': result.marketplace,
                'royalty_amount': result.royalty_amount,
                'royalty_rate': result.royalty_rate,
                'tier': result.tier,
                'delivery_cost': result.delivery_cost,
                'print_cost': result.print_cost,
            }
            console.print(json.dumps(data, indent=2))
            return

        table = Table(title=f'Royalty Calculator')
        table.add_column('Field', style='bold')
        table.add_column('Value')

        table.add_row('List Price', f'${result.price:.2f}')
        table.add_row('Format', result.format)
        table.add_row('Marketplace', result.marketplace)
        table.add_row('Tier', result.tier)
        table.add_row('Royalty Rate', f'{result.royalty_rate:.0%}')
        if result.delivery_cost > 0:
            table.add_row('Delivery Cost', f'${result.delivery_cost:.2f}')
        if result.print_cost > 0:
            table.add_row('Print Cost', f'${result.print_cost:.2f}')
        table.add_row('Royalty Amount', f'[green bold]${result.royalty_amount:.2f}[/green bold]')

        console.print(table)

    def format_royalty_comparison(self, results):
        """Show royalty at multiple price points for comparison."""
        if self.format == 'json':
            data = [
                {
                    'price': r.price,
                    'tier': r.tier,
                    'royalty_amount': r.royalty_amount,
                    'royalty_rate': r.royalty_rate,
                }
                for r in results
            ]
            console.print(json.dumps(data, indent=2))
            return

        table = Table(title='Royalty Comparison')
        table.add_column('Price', justify='right', style='bold')
        table.add_column('Tier')
        table.add_column('Rate', justify='right')
        table.add_column('Royalty', justify='right', style='green bold')

        for r in results:
            table.add_row(
                f'${r.price:.2f}', r.tier,
                f'{r.royalty_rate:.0%}', f'${r.royalty_amount:.2f}',
            )

        console.print(table)

    def format_experiments(self, experiments, schedules=None):
        if self.format == 'json':
            data = [
                {
                    'asin': e.asin,
                    'prices': e.prices,
                    'duration_days': e.duration_days,
                    'started_at': e.started_at,
                    'current_price_index': e.current_price_index,
                    'status': e.status,
                    'schedule': schedules.get(e.asin, []) if schedules else [],
                }
                for e in experiments
            ]
            console.print(json.dumps(data, indent=2))
            return

        if not experiments:
            console.print('[dim]No experiments found.[/dim]')
            return

        for exp in experiments:
            status_style = {
                'running': 'green',
                'completed': 'cyan',
                'cancelled': 'red',
            }.get(exp.status, 'dim')

            table = Table(title=f'Experiment: {exp.asin} [{status_style}]{exp.status}[/{status_style}]')
            table.add_column('Price', justify='right', style='bold')
            table.add_column('Start', style='dim')
            table.add_column('End', style='dim')
            table.add_column('Status')

            schedule = schedules.get(exp.asin, []) if schedules else []
            if schedule:
                for period in schedule:
                    pstyle = 'bold green' if period['status'] == 'active' else 'dim'
                    table.add_row(
                        f'${period["price"]:.2f}',
                        period['start_date'], period['end_date'],
                        f'[{pstyle}]{period["status"]}[/{pstyle}]',
                    )
            else:
                for i, price in enumerate(exp.prices):
                    marker = ' (current)' if i == exp.current_price_index else ''
                    table.add_row(f'${price:.2f}', '', '', marker)

            console.print(table)
            console.print()
