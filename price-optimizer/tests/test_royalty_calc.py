"""Tests for KDP royalty calculator. CRITICAL — correctness is paramount."""

import pytest
from price_optimizer.royalty_calc import (
    calculate_royalty, calculate_all_tiers,
    DELIVERY_COST_PER_MB, PAPERBACK_BW_PER_PAGE, PAPERBACK_FIXED_COST,
    PAPERBACK_COLOR_PER_PAGE, HARDCOVER_FIXED_COST,
)


class TestEbook70Percent:
    """70% royalty tier: $2.99-$9.99 (US), minus delivery cost."""

    def test_at_299(self):
        r = calculate_royalty(2.99)
        assert r.tier == '70%'
        assert r.royalty_rate == 0.70
        expected = round(2.99 * 0.70 - 0.5 * DELIVERY_COST_PER_MB, 2)
        assert r.royalty_amount == expected

    def test_at_499(self):
        r = calculate_royalty(4.99)
        assert r.tier == '70%'
        expected = round(4.99 * 0.70 - 0.5 * DELIVERY_COST_PER_MB, 2)
        assert r.royalty_amount == expected

    def test_at_999(self):
        r = calculate_royalty(9.99)
        assert r.tier == '70%'
        expected = round(9.99 * 0.70 - 0.5 * DELIVERY_COST_PER_MB, 2)
        assert r.royalty_amount == expected

    def test_delivery_cost_deducted(self):
        r = calculate_royalty(4.99, delivery_mb=1.0)
        assert r.delivery_cost == round(1.0 * DELIVERY_COST_PER_MB, 2)
        expected = round(4.99 * 0.70 - 1.0 * DELIVERY_COST_PER_MB, 2)
        assert r.royalty_amount == expected

    def test_delivery_cost_zero_mb(self):
        r = calculate_royalty(4.99, delivery_mb=0.0)
        assert r.delivery_cost == 0.0
        assert r.royalty_amount == round(4.99 * 0.70, 2)

    def test_large_delivery_cost_floors_at_zero(self):
        """If delivery cost exceeds royalty, floor at $0."""
        r = calculate_royalty(2.99, delivery_mb=100.0)
        assert r.royalty_amount == 0.0
        assert r.tier == '70%'

    def test_default_delivery_mb(self):
        """Default delivery is 0.5 MB."""
        r = calculate_royalty(4.99)
        assert r.delivery_cost == round(0.5 * DELIVERY_COST_PER_MB, 2)


class TestEbook35Percent:
    """35% royalty tier: any price, no delivery cost."""

    def test_at_099(self):
        r = calculate_royalty(0.99)
        assert r.tier == '35%'
        assert r.royalty_rate == 0.35
        assert r.royalty_amount == round(0.99 * 0.35, 2)

    def test_at_199(self):
        r = calculate_royalty(1.99)
        assert r.tier == '35%'
        assert r.royalty_amount == round(1.99 * 0.35, 2)

    def test_at_1499(self):
        r = calculate_royalty(14.99)
        assert r.tier == '35%'
        assert r.royalty_amount == round(14.99 * 0.35, 2)

    def test_no_delivery_cost(self):
        r = calculate_royalty(0.99)
        assert r.delivery_cost == 0.0


class TestEbookTierBoundaries:
    """Exact boundary behavior is critical."""

    def test_298_is_35_percent(self):
        r = calculate_royalty(2.98)
        assert r.tier == '35%'

    def test_299_is_70_percent(self):
        r = calculate_royalty(2.99)
        assert r.tier == '70%'

    def test_999_is_70_percent(self):
        r = calculate_royalty(9.99)
        assert r.tier == '70%'

    def test_1000_is_35_percent(self):
        r = calculate_royalty(10.00)
        assert r.tier == '35%'

    def test_300_is_70_percent(self):
        r = calculate_royalty(3.00)
        assert r.tier == '70%'

    def test_998_is_70_percent(self):
        r = calculate_royalty(9.98)
        assert r.tier == '70%'


class TestPaperback:
    """Paperback: 60% x (list price - printing cost)."""

    def test_with_explicit_print_cost(self):
        r = calculate_royalty(14.99, format='paperback', print_cost=4.50)
        assert r.tier == 'paperback'
        assert r.royalty_rate == 0.60
        expected = round(0.60 * (14.99 - 4.50), 2)
        assert r.royalty_amount == expected
        assert r.print_cost == 4.50

    def test_with_page_count_bw(self):
        r = calculate_royalty(14.99, format='paperback', page_count=300)
        expected_cost = round(PAPERBACK_FIXED_COST + 300 * PAPERBACK_BW_PER_PAGE, 2)
        expected_royalty = round(0.60 * (14.99 - expected_cost), 2)
        assert r.print_cost == expected_cost
        assert r.royalty_amount == expected_royalty

    def test_with_page_count_color(self):
        r = calculate_royalty(24.99, format='paperback', page_count=200, color=True)
        expected_cost = round(PAPERBACK_FIXED_COST + 200 * PAPERBACK_COLOR_PER_PAGE, 2)
        expected_royalty = round(0.60 * (24.99 - expected_cost), 2)
        assert r.print_cost == expected_cost
        assert r.royalty_amount == expected_royalty

    def test_no_cost_info(self):
        """Without page count or print cost, royalty is 0."""
        r = calculate_royalty(14.99, format='paperback')
        assert r.royalty_amount == 0.0
        assert r.royalty_rate == 0.60

    def test_price_below_print_cost(self):
        """If price < print cost, royalty floors at 0."""
        r = calculate_royalty(2.00, format='paperback', print_cost=4.50)
        assert r.royalty_amount == 0.0

    def test_real_world_example(self):
        """300-page B&W paperback at $14.99."""
        r = calculate_royalty(14.99, format='paperback', page_count=300)
        assert r.royalty_amount > 0
        assert r.print_cost > 0
        # Sanity check: royalty should be reasonable
        assert 2.0 < r.royalty_amount < 10.0


class TestHardcover:
    """Hardcover: 40% x (list price - printing cost)."""

    def test_with_explicit_print_cost(self):
        r = calculate_royalty(24.99, format='hardcover', print_cost=10.00)
        assert r.tier == 'hardcover'
        assert r.royalty_rate == 0.40
        expected = round(0.40 * (24.99 - 10.00), 2)
        assert r.royalty_amount == expected

    def test_with_page_count(self):
        r = calculate_royalty(29.99, format='hardcover', page_count=300)
        expected_cost = round(HARDCOVER_FIXED_COST + 300 * 0.012, 2)
        expected_royalty = round(0.40 * (29.99 - expected_cost), 2)
        assert r.royalty_amount == expected_royalty

    def test_price_below_print_cost(self):
        r = calculate_royalty(5.00, format='hardcover', print_cost=10.00)
        assert r.royalty_amount == 0.0


class TestMarketplaces:
    """Test marketplace-specific 70% tier bounds."""

    def test_uk_199_is_70_percent(self):
        r = calculate_royalty(1.99, marketplace='UK')
        assert r.tier == '70%'

    def test_uk_198_is_35_percent(self):
        r = calculate_royalty(1.98, marketplace='UK')
        assert r.tier == '35%'

    def test_uk_699_is_70_percent(self):
        r = calculate_royalty(6.99, marketplace='UK')
        assert r.tier == '70%'

    def test_uk_700_is_35_percent(self):
        r = calculate_royalty(7.00, marketplace='UK')
        assert r.tier == '35%'

    def test_jp_250_is_70_percent(self):
        r = calculate_royalty(250, marketplace='JP')
        assert r.tier == '70%'

    def test_jp_249_is_35_percent(self):
        r = calculate_royalty(249, marketplace='JP')
        assert r.tier == '35%'

    def test_unknown_marketplace_uses_35(self):
        r = calculate_royalty(4.99, marketplace='ZZ')
        assert r.tier == '35%'

    def test_de_marketplace(self):
        r = calculate_royalty(4.99, marketplace='DE')
        assert r.tier == '70%'

    def test_in_marketplace_bounds(self):
        r = calculate_royalty(100, marketplace='IN')
        assert r.tier == '70%'

    def test_in_marketplace_below_bound(self):
        r = calculate_royalty(48, marketplace='IN')
        assert r.tier == '35%'


class TestEdgeCases:
    """Edge cases and error handling."""

    def test_free_book(self):
        r = calculate_royalty(0.0)
        assert r.royalty_amount == 0.0
        assert r.tier == 'free'

    def test_negative_price(self):
        r = calculate_royalty(-1.00)
        assert r.royalty_amount == 0.0
        assert r.tier == 'invalid'

    def test_none_price(self):
        r = calculate_royalty(None)
        assert r.royalty_amount == 0.0
        assert r.tier == 'invalid'

    def test_very_high_price(self):
        r = calculate_royalty(999.99)
        assert r.tier == '35%'
        assert r.royalty_amount == round(999.99 * 0.35, 2)

    def test_one_cent(self):
        r = calculate_royalty(0.01)
        assert r.tier == '35%'
        assert r.royalty_amount == round(0.01 * 0.35, 2)

    def test_unknown_format_defaults_to_ebook(self):
        r = calculate_royalty(4.99, format='audiobook')
        assert r.tier == '70%'  # Treated as ebook

    def test_case_insensitive_format(self):
        r = calculate_royalty(14.99, format='Paperback', print_cost=4.50)
        assert r.tier == 'paperback'

    def test_marketplace_case_insensitive(self):
        r = calculate_royalty(4.99, marketplace='us')
        assert r.tier == '70%'


class TestCalculateAllTiers:
    """Test the tier comparison utility."""

    def test_returns_both_tiers(self):
        result = calculate_all_tiers(4.99)
        assert '35%' in result
        assert '70%' in result

    def test_35_tier_no_delivery(self):
        result = calculate_all_tiers(4.99)
        assert result['35%'].royalty_amount == round(4.99 * 0.35, 2)

    def test_70_tier_with_delivery(self):
        result = calculate_all_tiers(4.99, delivery_mb=0.5)
        expected = round(4.99 * 0.70 - 0.5 * DELIVERY_COST_PER_MB, 2)
        assert result['70%'].royalty_amount == expected

    def test_70_always_better_in_range(self):
        """At $4.99, 70% tier should always yield more than 35%."""
        result = calculate_all_tiers(4.99)
        assert result['70%'].royalty_amount > result['35%'].royalty_amount
