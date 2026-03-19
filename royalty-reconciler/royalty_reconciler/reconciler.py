"""Core reconciliation engine.

Groups sales by platform+month, compares expected royalties vs received payments,
and generates P&L reports.
"""
import logging
from collections import defaultdict
from typing import List

from .models import PnLReport, ReconciliationResult
from .currency import convert_to_usd

logger = logging.getLogger(__name__)

# Tolerance for matching expected vs received payments (in USD)
MATCH_TOLERANCE = 0.50


def build_pnl(sales: List[dict], expenses: List[dict], period: str) -> PnLReport:
    """Build a profit & loss report from sales and expenses.

    Args:
        sales: List of sale dicts from the database
        expenses: List of expense dicts from the database
        period: Period label (e.g., '2026-03' or '2025')

    Returns:
        PnLReport with all calculations
    """
    report = PnLReport(period=period)

    by_platform = defaultdict(lambda: {'royalties': 0.0, 'refunds': 0.0, 'units': 0})
    by_book = defaultdict(lambda: {'royalties': 0.0, 'refunds': 0.0, 'units': 0, 'title': ''})

    for s in sales:
        royalty_usd = convert_to_usd(s.get('royalty_amount', 0.0),
                                      s.get('currency', 'USD'),
                                      s.get('date'))
        refund_usd = convert_to_usd(s.get('refund_amount', 0.0),
                                     s.get('currency', 'USD'),
                                     s.get('date'))
        platform = s.get('platform', 'kdp')
        book_id = s.get('book_id', 0)
        title = s.get('title', f'Book #{book_id}')

        report.gross_royalties += royalty_usd
        report.refunds += refund_usd

        by_platform[platform]['royalties'] += royalty_usd
        by_platform[platform]['refunds'] += refund_usd
        by_platform[platform]['units'] += s.get('units', 0)

        by_book[book_id]['royalties'] += royalty_usd
        by_book[book_id]['refunds'] += refund_usd
        by_book[book_id]['units'] += s.get('units', 0)
        by_book[book_id]['title'] = title

    report.net_royalties = round(report.gross_royalties - report.refunds, 2)
    report.gross_royalties = round(report.gross_royalties, 2)
    report.refunds = round(report.refunds, 2)

    # Process expenses
    expense_breakdown = defaultdict(float)
    for e in expenses:
        amount_usd = convert_to_usd(e.get('amount', 0.0),
                                     e.get('currency', 'USD'),
                                     e.get('date'))
        report.total_expenses += amount_usd
        expense_breakdown[e.get('category', 'other')] += amount_usd

    report.total_expenses = round(report.total_expenses, 2)
    report.net_profit = round(report.net_royalties - report.total_expenses, 2)

    # Round sub-dicts
    report.by_platform = {
        k: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()}
        for k, v in by_platform.items()
    }
    report.by_book = {
        k: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()}
        for k, v in by_book.items()
    }
    report.expense_breakdown = {k: round(v, 2) for k, v in expense_breakdown.items()}

    return report


def reconcile_month(sales: List[dict], month: str) -> List[ReconciliationResult]:
    """Reconcile expected vs received payments for a given month.

    Groups sales by platform and checks if payment_received flag is set.

    Args:
        sales: List of sale dicts for the month
        month: Month label (e.g., '2026-03')

    Returns:
        List of ReconciliationResult per platform
    """
    by_platform = defaultdict(lambda: {
        'expected': 0.0, 'received': 0.0, 'records': 0,
        'paid_records': 0
    })

    for s in sales:
        platform = s.get('platform', 'kdp')
        royalty_usd = convert_to_usd(s.get('royalty_amount', 0.0),
                                      s.get('currency', 'USD'),
                                      s.get('date'))
        refund_usd = convert_to_usd(s.get('refund_amount', 0.0),
                                     s.get('currency', 'USD'),
                                     s.get('date'))
        net = royalty_usd - refund_usd

        by_platform[platform]['expected'] += net
        by_platform[platform]['records'] += 1

        if s.get('payment_received'):
            by_platform[platform]['received'] += net
            by_platform[platform]['paid_records'] += 1

    results = []
    for platform, data in sorted(by_platform.items()):
        expected = round(data['expected'], 2)
        received = round(data['received'], 2)
        discrepancy = round(received - expected, 2)

        if data['paid_records'] == 0:
            status = 'pending'
        elif abs(discrepancy) <= MATCH_TOLERANCE:
            status = 'matched'
        elif discrepancy < 0:
            status = 'underpaid'
        else:
            status = 'overpaid'

        results.append(ReconciliationResult(
            platform=platform,
            month=month,
            expected_royalties=expected,
            received_payment=received,
            discrepancy=discrepancy,
            status=status,
            records=data['records'],
        ))

    return results
