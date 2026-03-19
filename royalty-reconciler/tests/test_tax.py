"""Tests for the tax module."""
import pytest

from royalty_reconciler.tax import generate_tax_report, export_tax_csv, _categorize_expense


class TestCategorizeExpense:
    def test_ads_category(self):
        assert _categorize_expense('ads') == 'advertising'
        assert _categorize_expense('advertising') == 'advertising'
        assert _categorize_expense('marketing') == 'advertising'

    def test_contract_labor_category(self):
        assert _categorize_expense('editing') == 'contract_labor'
        assert _categorize_expense('cover') == 'contract_labor'
        assert _categorize_expense('formatting') == 'contract_labor'
        assert _categorize_expense('proofreading') == 'contract_labor'
        assert _categorize_expense('narration') == 'contract_labor'

    def test_office_expenses_category(self):
        assert _categorize_expense('tools') == 'office_expenses'
        assert _categorize_expense('software') == 'office_expenses'
        assert _categorize_expense('hosting') == 'office_expenses'

    def test_other_expenses_category(self):
        assert _categorize_expense('isbn') == 'other_expenses'
        assert _categorize_expense('copyright') == 'other_expenses'
        assert _categorize_expense('travel') == 'other_expenses'

    def test_unknown_maps_to_other(self):
        assert _categorize_expense('random_thing') == 'other_expenses'

    def test_case_insensitive(self):
        assert _categorize_expense('ADS') == 'advertising'
        assert _categorize_expense('Editing') == 'contract_labor'


class TestGenerateTaxReport:
    def test_basic_report(self):
        sales = [
            {'royalty_amount': 100.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2025-06-01', 'platform': 'kdp'},
        ]
        expenses = []
        report = generate_tax_report(sales, expenses, 2025)
        assert report.year == 2025
        assert report.gross_receipts == 100.0
        assert report.net_profit == 100.0

    def test_report_with_refunds(self):
        sales = [
            {'royalty_amount': 100.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2025-06-01', 'platform': 'kdp'},
            {'royalty_amount': 0.0, 'refund_amount': 10.0, 'currency': 'USD',
             'date': '2025-06-15', 'platform': 'kdp'},
        ]
        report = generate_tax_report(sales, [], 2025)
        assert report.returns_allowances == 10.0
        assert report.net_profit == 90.0

    def test_report_with_expenses(self):
        sales = [
            {'royalty_amount': 1000.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2025-06-01', 'platform': 'kdp'},
        ]
        expenses = [
            {'amount': 200.0, 'currency': 'USD', 'date': '2025-01-01', 'category': 'ads'},
            {'amount': 500.0, 'currency': 'USD', 'date': '2025-02-01', 'category': 'editing'},
            {'amount': 50.0, 'currency': 'USD', 'date': '2025-03-01', 'category': 'software'},
            {'amount': 30.0, 'currency': 'USD', 'date': '2025-04-01', 'category': 'isbn'},
        ]
        report = generate_tax_report(sales, expenses, 2025)
        assert report.advertising == 200.0
        assert report.contract_labor == 500.0
        assert report.office_expenses == 50.0
        assert report.other_expenses == 30.0
        assert report.total_expenses == 780.0
        assert report.net_profit == 220.0

    def test_platform_breakdown(self):
        sales = [
            {'royalty_amount': 100.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2025-06-01', 'platform': 'kdp'},
            {'royalty_amount': 50.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2025-06-01', 'platform': 'apple'},
        ]
        report = generate_tax_report(sales, [], 2025)
        assert 'kdp' in report.platform_breakdown
        assert 'apple' in report.platform_breakdown
        assert report.platform_breakdown['kdp']['gross'] == 100.0
        assert report.platform_breakdown['apple']['gross'] == 50.0

    def test_other_expense_details(self):
        expenses = [
            {'amount': 30.0, 'currency': 'USD', 'date': '2025-04-01',
             'category': 'isbn', 'description': 'ISBN purchase'},
        ]
        report = generate_tax_report([], expenses, 2025)
        assert len(report.other_expense_details) == 1
        assert report.other_expense_details[0]['description'] == 'ISBN purchase'

    def test_empty_report(self):
        report = generate_tax_report([], [], 2025)
        assert report.gross_receipts == 0.0
        assert report.total_expenses == 0.0
        assert report.net_profit == 0.0

    def test_negative_net_profit(self):
        expenses = [
            {'amount': 500.0, 'currency': 'USD', 'date': '2025-01-01', 'category': 'ads'},
        ]
        report = generate_tax_report([], expenses, 2025)
        assert report.net_profit == -500.0


class TestExportTaxCSV:
    def test_csv_export(self):
        sales = [
            {'royalty_amount': 100.0, 'refund_amount': 5.0, 'currency': 'USD',
             'date': '2025-06-01', 'platform': 'kdp'},
        ]
        expenses = [
            {'amount': 50.0, 'currency': 'USD', 'date': '2025-01-01', 'category': 'ads'},
        ]
        report = generate_tax_report(sales, expenses, 2025)
        csv_content = export_tax_csv(report)

        assert 'Schedule C Summary' in csv_content
        assert 'Tax Year 2025' in csv_content
        assert 'Gross receipts' in csv_content
        assert 'Advertising' in csv_content
        assert '100.00' in csv_content

    def test_csv_contains_platform_breakdown(self):
        sales = [
            {'royalty_amount': 100.0, 'refund_amount': 0.0, 'currency': 'USD',
             'date': '2025-06-01', 'platform': 'kdp'},
        ]
        report = generate_tax_report(sales, [], 2025)
        csv_content = export_tax_csv(report)
        assert 'INCOME BY PLATFORM' in csv_content
        assert 'kdp' in csv_content

    def test_csv_export_empty(self):
        report = generate_tax_report([], [], 2025)
        csv_content = export_tax_csv(report)
        assert 'Schedule C Summary' in csv_content
        assert '0.00' in csv_content
