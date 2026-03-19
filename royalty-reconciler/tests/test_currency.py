"""Tests for the currency module."""
import pytest

from royalty_reconciler.currency import (
    get_exchange_rate,
    convert_to_usd,
    STATIC_RATES_TO_USD,
)


class TestGetExchangeRate:
    def test_same_currency(self):
        assert get_exchange_rate('USD', 'USD') == 1.0

    def test_same_currency_case_insensitive(self):
        assert get_exchange_rate('usd', 'USD') == 1.0

    def test_gbp_to_usd_static(self):
        rate = get_exchange_rate('GBP', 'USD')
        assert rate > 1.0  # GBP is worth more than USD
        assert rate == STATIC_RATES_TO_USD['GBP'] / STATIC_RATES_TO_USD['USD']

    def test_eur_to_usd_static(self):
        rate = get_exchange_rate('EUR', 'USD')
        assert rate > 1.0

    def test_jpy_to_usd_static(self):
        rate = get_exchange_rate('JPY', 'USD')
        assert rate < 0.1  # JPY is much less than USD

    def test_usd_to_gbp_static(self):
        rate = get_exchange_rate('USD', 'GBP')
        assert rate < 1.0  # Need less GBP for 1 USD

    def test_unknown_currency_returns_one(self):
        rate = get_exchange_rate('XYZ', 'USD')
        assert rate == 1.0

    def test_cross_rate(self):
        # GBP -> EUR should work via USD
        rate = get_exchange_rate('GBP', 'EUR')
        assert rate > 0

    def test_cad_to_usd(self):
        rate = get_exchange_rate('CAD', 'USD')
        assert 0.5 < rate < 1.0


class TestConvertToUSD:
    def test_usd_passthrough(self):
        assert convert_to_usd(10.0, 'USD') == 10.0

    def test_gbp_conversion(self):
        result = convert_to_usd(10.0, 'GBP')
        assert result > 10.0  # GBP worth more than USD
        expected = round(10.0 * STATIC_RATES_TO_USD['GBP'], 2)
        assert result == expected

    def test_eur_conversion(self):
        result = convert_to_usd(100.0, 'EUR')
        assert result > 100.0

    def test_zero_amount(self):
        assert convert_to_usd(0.0, 'GBP') == 0.0

    def test_negative_amount(self):
        result = convert_to_usd(-5.0, 'GBP')
        assert result < 0

    def test_rounding(self):
        result = convert_to_usd(1.0, 'GBP')
        # Should be rounded to 2 decimal places
        assert result == round(result, 2)

    def test_cad_conversion(self):
        result = convert_to_usd(10.0, 'CAD')
        assert result < 10.0  # CAD worth less than USD

    def test_case_insensitive(self):
        assert convert_to_usd(10.0, 'usd') == 10.0


class TestStaticRates:
    def test_major_currencies_present(self):
        for currency in ['USD', 'GBP', 'EUR', 'CAD', 'AUD', 'JPY']:
            assert currency in STATIC_RATES_TO_USD

    def test_usd_is_one(self):
        assert STATIC_RATES_TO_USD['USD'] == 1.0

    def test_all_rates_positive(self):
        for currency, rate in STATIC_RATES_TO_USD.items():
            assert rate > 0, f"{currency} rate should be positive"
