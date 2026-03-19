"""Schedule C tax report generation.

Maps expense categories to Schedule C line items and generates
formatted reports for tax filing.
"""
import csv
import logging
from io import StringIO
from typing import List

from .models import TaxReport
from .currency import convert_to_usd

logger = logging.getLogger(__name__)

# Map expense categories to Schedule C categories
SCHEDULE_C_MAP = {
    # Advertising (Line 8)
    'ads': 'advertising',
    'advertising': 'advertising',
    'marketing': 'advertising',
    'promo': 'advertising',
    'promotion': 'advertising',
    'bookbub': 'advertising',
    'ams': 'advertising',

    # Contract labor (Line 11)
    'editing': 'contract_labor',
    'editor': 'contract_labor',
    'cover': 'contract_labor',
    'cover design': 'contract_labor',
    'formatting': 'contract_labor',
    'proofreading': 'contract_labor',
    'narration': 'contract_labor',
    'illustration': 'contract_labor',
    'freelance': 'contract_labor',

    # Office expenses (Line 18)
    'tools': 'office_expenses',
    'software': 'office_expenses',
    'office': 'office_expenses',
    'supplies': 'office_expenses',
    'equipment': 'office_expenses',
    'subscription': 'office_expenses',
    'hosting': 'office_expenses',
    'domain': 'office_expenses',

    # Other expenses (Line 27a)
    'isbn': 'other_expenses',
    'copyright': 'other_expenses',
    'legal': 'other_expenses',
    'travel': 'other_expenses',
    'conference': 'other_expenses',
    'education': 'other_expenses',
    'research': 'other_expenses',
    'misc': 'other_expenses',
    'other': 'other_expenses',
}


def _categorize_expense(category: str) -> str:
    """Map an expense category to a Schedule C category."""
    return SCHEDULE_C_MAP.get(category.lower().strip(), 'other_expenses')


def generate_tax_report(sales: List[dict], expenses: List[dict],
                        year: int) -> TaxReport:
    """Generate a Schedule C tax report for a given year.

    Args:
        sales: List of sale dicts for the year
        expenses: List of expense dicts for the year
        year: Tax year

    Returns:
        TaxReport with Schedule C categorization
    """
    report = TaxReport(year=year)

    # Calculate gross receipts by platform
    platform_totals = {}
    for s in sales:
        platform = s.get('platform', 'kdp')
        royalty_usd = convert_to_usd(s.get('royalty_amount', 0.0),
                                      s.get('currency', 'USD'),
                                      s.get('date'))
        refund_usd = convert_to_usd(s.get('refund_amount', 0.0),
                                     s.get('currency', 'USD'),
                                     s.get('date'))

        if platform not in platform_totals:
            platform_totals[platform] = {'gross': 0.0, 'refunds': 0.0}
        platform_totals[platform]['gross'] += royalty_usd
        platform_totals[platform]['refunds'] += refund_usd

    report.platform_breakdown = {
        k: {kk: round(vv, 2) for kk, vv in v.items()}
        for k, v in platform_totals.items()
    }
    report.gross_receipts = round(
        sum(v['gross'] for v in platform_totals.values()), 2
    )
    report.returns_allowances = round(
        sum(v['refunds'] for v in platform_totals.values()), 2
    )

    # Categorize expenses
    for e in expenses:
        amount_usd = convert_to_usd(e.get('amount', 0.0),
                                     e.get('currency', 'USD'),
                                     e.get('date'))
        sched_c_cat = _categorize_expense(e.get('category', 'other'))

        if sched_c_cat == 'advertising':
            report.advertising += amount_usd
        elif sched_c_cat == 'contract_labor':
            report.contract_labor += amount_usd
        elif sched_c_cat == 'office_expenses':
            report.office_expenses += amount_usd
        else:
            report.other_expenses += amount_usd
            report.other_expense_details.append({
                'date': e.get('date', ''),
                'amount': round(amount_usd, 2),
                'category': e.get('category', 'other'),
                'description': e.get('description', ''),
            })

    # Round and total
    report.advertising = round(report.advertising, 2)
    report.contract_labor = round(report.contract_labor, 2)
    report.office_expenses = round(report.office_expenses, 2)
    report.other_expenses = round(report.other_expenses, 2)
    report.total_expenses = round(
        report.advertising + report.contract_labor +
        report.office_expenses + report.other_expenses, 2
    )
    report.net_profit = round(
        report.gross_receipts - report.returns_allowances - report.total_expenses, 2
    )

    return report


def export_tax_csv(report: TaxReport) -> str:
    """Export a tax report as CSV string."""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['Schedule C Summary', f'Tax Year {report.year}'])
    writer.writerow([])
    writer.writerow(['Line', 'Description', 'Amount'])
    writer.writerow(['1', 'Gross receipts', f'{report.gross_receipts:.2f}'])
    writer.writerow(['2', 'Returns and allowances', f'{report.returns_allowances:.2f}'])
    writer.writerow(['3', 'Net receipts (Line 1 - Line 2)',
                     f'{report.gross_receipts - report.returns_allowances:.2f}'])
    writer.writerow([])
    writer.writerow(['', 'EXPENSES', ''])
    writer.writerow(['8', 'Advertising', f'{report.advertising:.2f}'])
    writer.writerow(['11', 'Contract labor', f'{report.contract_labor:.2f}'])
    writer.writerow(['18', 'Office expenses', f'{report.office_expenses:.2f}'])
    writer.writerow(['27a', 'Other expenses', f'{report.other_expenses:.2f}'])
    writer.writerow(['28', 'Total expenses', f'{report.total_expenses:.2f}'])
    writer.writerow([])
    writer.writerow(['31', 'Net profit (or loss)', f'{report.net_profit:.2f}'])

    if report.platform_breakdown:
        writer.writerow([])
        writer.writerow(['', 'INCOME BY PLATFORM', ''])
        writer.writerow(['Platform', 'Gross', 'Refunds', 'Net'])
        for platform, data in sorted(report.platform_breakdown.items()):
            net = data['gross'] - data['refunds']
            writer.writerow([platform, f'{data["gross"]:.2f}',
                           f'{data["refunds"]:.2f}', f'{net:.2f}'])

    if report.other_expense_details:
        writer.writerow([])
        writer.writerow(['', 'OTHER EXPENSE DETAILS', ''])
        writer.writerow(['Date', 'Category', 'Amount', 'Description'])
        for d in report.other_expense_details:
            writer.writerow([d['date'], d['category'],
                           f'{d["amount"]:.2f}', d['description']])

    return output.getvalue()
