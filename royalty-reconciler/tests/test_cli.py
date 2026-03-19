"""Tests for the CLI commands."""
import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from royalty_reconciler.cli import main

FIXTURES = Path(__file__).parent / 'fixtures'


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_db_path():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    os.unlink(path)


class TestCLIVersion:
    def test_version(self, runner):
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert '0.1.0' in result.output


class TestCLIConfig:
    def test_config(self, runner):
        result = runner.invoke(main, ['config'])
        assert result.exit_code == 0
        assert 'DB_PATH' in result.output


class TestCLIImport:
    def test_import_kdp(self, runner, tmp_db_path):
        # First we need a book in the DB - import without ASIN
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'kdp_sales.csv'),
            '--platform', 'kdp',
        ])
        assert result.exit_code == 0
        assert 'Imported' in result.output

    def test_import_with_asin_no_book(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'kdp_sales.csv'),
            '--platform', 'kdp',
            '--asin', 'B0NONEXIST',
        ])
        assert result.exit_code == 0
        assert 'No book found' in result.output

    def test_import_auto_detect_kdp(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'kdp_sales.csv'),
        ])
        assert result.exit_code == 0
        assert 'Auto-detected' in result.output or 'Imported' in result.output

    def test_import_apple(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'apple_sales.csv'),
            '--platform', 'apple',
        ])
        assert result.exit_code == 0
        assert 'Imported' in result.output

    def test_import_kobo(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'kobo_sales.csv'),
            '--platform', 'kobo',
        ])
        assert result.exit_code == 0

    def test_import_google(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'google_sales.csv'),
            '--platform', 'google',
        ])
        assert result.exit_code == 0

    def test_import_d2d(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'd2d_sales.csv'),
            '--platform', 'd2d',
        ])
        assert result.exit_code == 0

    def test_import_acx(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'acx_sales.csv'),
            '--platform', 'acx',
        ])
        assert result.exit_code == 0

    def test_import_json_output(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            '-o', 'json',
            'import', str(FIXTURES / 'kdp_sales.csv'),
            '--platform', 'kdp',
        ])
        assert result.exit_code == 0


class TestCLIAddExpense:
    def test_add_expense(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'add-expense',
            '--amount', '50',
            '--category', 'ads',
            '--date', '2026-03-01',
            '--description', 'AMS campaign',
        ])
        assert result.exit_code == 0
        assert 'Added expense' in result.output
        assert '50.00' in result.output

    def test_add_expense_json(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            '-o', 'json',
            'add-expense',
            '--amount', '100',
            '--category', 'editing',
            '--date', '2026-03-05',
        ])
        assert result.exit_code == 0
        assert '"amount"' in result.output


class TestCLIPnL:
    def test_pnl_no_args(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'pnl',
        ])
        assert result.exit_code == 0
        assert 'Specify' in result.output

    def test_pnl_by_month(self, runner, tmp_db_path):
        # Import data first
        runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'kdp_sales.csv'),
            '--platform', 'kdp',
        ])
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'pnl', '--month', '2026-03',
        ])
        assert result.exit_code == 0

    def test_pnl_by_year(self, runner, tmp_db_path):
        runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'kdp_sales.csv'),
            '--platform', 'kdp',
        ])
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'pnl', '--year', '2026',
        ])
        assert result.exit_code == 0

    def test_pnl_json(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            '-o', 'json',
            'pnl', '--month', '2026-03',
        ])
        assert result.exit_code == 0


class TestCLITax:
    def test_tax_report(self, runner, tmp_db_path):
        runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'kdp_sales.csv'),
            '--platform', 'kdp',
        ])
        runner.invoke(main, [
            '--db', tmp_db_path,
            'add-expense', '--amount', '50', '--category', 'ads',
            '--date', '2026-03-01',
        ])
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'tax', '--year', '2026',
        ])
        assert result.exit_code == 0

    def test_tax_export(self, runner, tmp_db_path, tmp_path):
        export_file = str(tmp_path / 'schedule_c.csv')
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'tax', '--year', '2026', '--export', export_file,
        ])
        assert result.exit_code == 0
        assert os.path.exists(export_file)

    def test_tax_json(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            '-o', 'json',
            'tax', '--year', '2026',
        ])
        assert result.exit_code == 0


class TestCLIReconcile:
    def test_reconcile(self, runner, tmp_db_path):
        runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'kdp_sales.csv'),
            '--platform', 'kdp',
        ])
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'reconcile', '--month', '2026-03',
        ])
        assert result.exit_code == 0

    def test_reconcile_bad_format(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'reconcile', '--month', 'March',
        ])
        assert result.exit_code == 0
        assert 'YYYY-MM' in result.output

    def test_reconcile_json(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            '-o', 'json',
            'reconcile', '--month', '2026-03',
        ])
        assert result.exit_code == 0


class TestCLIStatus:
    def test_status_empty(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'status',
        ])
        assert result.exit_code == 0

    def test_status_after_import(self, runner, tmp_db_path):
        runner.invoke(main, [
            '--db', tmp_db_path,
            'import', str(FIXTURES / 'kdp_sales.csv'),
            '--platform', 'kdp',
        ])
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            'status',
        ])
        assert result.exit_code == 0

    def test_status_json(self, runner, tmp_db_path):
        result = runner.invoke(main, [
            '--db', tmp_db_path,
            '-o', 'json',
            'status',
        ])
        assert result.exit_code == 0
