"""Tests for the reconciliation engine."""
import pytest

from royalty_reconciler.reconciler import build_pnl, reconcile_month


class TestBuildPnL:
    def test_basic_pnl(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'book_id': 1,
             'title': 'Book A', 'units': 2},
            {'royalty_amount': 5.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-02', 'platform': 'kdp', 'book_id': 1,
             'title': 'Book A', 'units': 1},
        ]
        expenses = []
        report = build_pnl(sales, expenses, '2026-03')
        assert report.gross_royalties == 15.0
        assert report.refunds == 0.0
        assert report.net_royalties == 15.0
        assert report.net_profit == 15.0

    def test_pnl_with_refunds(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'book_id': 1,
             'title': 'Book A', 'units': 2},
            {'royalty_amount': 0.0, 'refund_amount': 3.82, 'currency': 'USD',
             'date': '2026-03-05', 'platform': 'kdp', 'book_id': 1,
             'title': 'Book A', 'units': 1},
        ]
        report = build_pnl(sales, [], '2026-03')
        assert report.gross_royalties == 10.0
        assert report.refunds == 3.82
        assert report.net_royalties == 6.18

    def test_pnl_with_expenses(self):
        sales = [
            {'royalty_amount': 100.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'book_id': 1,
             'title': 'Book A', 'units': 10},
        ]
        expenses = [
            {'amount': 30.0, 'currency': 'USD', 'date': '2026-03-01', 'category': 'ads'},
            {'amount': 20.0, 'currency': 'USD', 'date': '2026-03-05', 'category': 'tools'},
        ]
        report = build_pnl(sales, expenses, '2026-03')
        assert report.total_expenses == 50.0
        assert report.net_profit == 50.0

    def test_pnl_by_platform(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'book_id': 1,
             'title': 'Book A', 'units': 2},
            {'royalty_amount': 5.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'apple', 'book_id': 1,
             'title': 'Book A', 'units': 1},
        ]
        report = build_pnl(sales, [], '2026-03')
        assert 'kdp' in report.by_platform
        assert 'apple' in report.by_platform
        assert report.by_platform['kdp']['royalties'] == 10.0
        assert report.by_platform['apple']['royalties'] == 5.0

    def test_pnl_by_book(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'book_id': 1,
             'title': 'Book A', 'units': 2},
            {'royalty_amount': 5.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'book_id': 2,
             'title': 'Book B', 'units': 1},
        ]
        report = build_pnl(sales, [], '2026-03')
        assert 1 in report.by_book
        assert 2 in report.by_book
        assert report.by_book[1]['royalties'] == 10.0
        assert report.by_book[2]['royalties'] == 5.0

    def test_pnl_expense_breakdown(self):
        sales = [
            {'royalty_amount': 100.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'book_id': 1,
             'title': 'Book A', 'units': 10},
        ]
        expenses = [
            {'amount': 30.0, 'currency': 'USD', 'date': '2026-03-01', 'category': 'ads'},
            {'amount': 20.0, 'currency': 'USD', 'date': '2026-03-05', 'category': 'ads'},
            {'amount': 15.0, 'currency': 'USD', 'date': '2026-03-10', 'category': 'tools'},
        ]
        report = build_pnl(sales, expenses, '2026-03')
        assert report.expense_breakdown['ads'] == 50.0
        assert report.expense_breakdown['tools'] == 15.0

    def test_pnl_empty_sales(self):
        report = build_pnl([], [], '2026-03')
        assert report.gross_royalties == 0.0
        assert report.net_profit == 0.0

    def test_pnl_negative_profit(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'book_id': 1,
             'title': 'Book A', 'units': 1},
        ]
        expenses = [
            {'amount': 50.0, 'currency': 'USD', 'date': '2026-03-01', 'category': 'ads'},
        ]
        report = build_pnl(sales, expenses, '2026-03')
        assert report.net_profit == -40.0

    def test_pnl_period_label(self):
        report = build_pnl([], [], '2025')
        assert report.period == '2025'


class TestReconcileMonth:
    def test_pending_status(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'payment_received': False},
        ]
        results = reconcile_month(sales, '2026-03')
        assert len(results) == 1
        assert results[0].status == 'pending'
        assert results[0].expected_royalties == 10.0
        assert results[0].received_payment == 0.0

    def test_matched_status(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'payment_received': True},
        ]
        results = reconcile_month(sales, '2026-03')
        assert results[0].status == 'matched'

    def test_underpaid_status(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'payment_received': True},
            {'royalty_amount': 5.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-02', 'platform': 'kdp', 'payment_received': False},
        ]
        results = reconcile_month(sales, '2026-03')
        assert results[0].status == 'underpaid'

    def test_multiple_platforms(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'payment_received': True},
            {'royalty_amount': 5.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'apple', 'payment_received': False},
        ]
        results = reconcile_month(sales, '2026-03')
        assert len(results) == 2
        platforms = {r.platform for r in results}
        assert 'kdp' in platforms
        assert 'apple' in platforms

    def test_discrepancy_calculation(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'payment_received': True},
            {'royalty_amount': 5.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-02', 'platform': 'kdp', 'payment_received': False},
        ]
        results = reconcile_month(sales, '2026-03')
        kdp = results[0]
        assert kdp.expected_royalties == 15.0
        assert kdp.received_payment == 10.0
        assert kdp.discrepancy == -5.0

    def test_empty_sales(self):
        results = reconcile_month([], '2026-03')
        assert len(results) == 0

    def test_refunds_reduce_expected(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'payment_received': True},
            {'royalty_amount': 0.0, 'refund_amount': 3.0, 'currency': 'USD',
             'date': '2026-03-05', 'platform': 'kdp', 'payment_received': True},
        ]
        results = reconcile_month(sales, '2026-03')
        assert results[0].expected_royalties == 7.0

    def test_record_count(self):
        sales = [
            {'royalty_amount': 10.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-01', 'platform': 'kdp', 'payment_received': True},
            {'royalty_amount': 5.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2026-03-02', 'platform': 'kdp', 'payment_received': True},
        ]
        results = reconcile_month(sales, '2026-03')
        assert results[0].records == 2
