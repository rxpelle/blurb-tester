"""Tests for price elasticity analysis and revenue optimization."""

import pytest
from price_optimizer.optimizer import analyze_price_elasticity, recommend_price
from price_optimizer.db import PriceChange, Sale, Snapshot


class TestAnalyzePriceElasticity:
    """Test elasticity analysis with known data."""

    def test_with_two_price_points(self, price_history_db):
        db, book_id = price_history_db
        changes = db.get_price_changes(book_id)
        sales = db.get_sales(book_id)
        snapshots = db.get_snapshots(book_id)

        price_points, elasticity = analyze_price_elasticity(changes, sales, snapshots)

        assert len(price_points) == 2
        # First price point: $14.99
        assert price_points[0].price == 14.99
        assert price_points[0].total_units >= 2
        # Second price point: $4.99
        assert price_points[1].price == 4.99
        assert price_points[1].total_units > 0

    def test_bsr_averages(self, price_history_db):
        db, book_id = price_history_db
        changes = db.get_price_changes(book_id)
        sales = db.get_sales(book_id)
        snapshots = db.get_snapshots(book_id)

        price_points, _ = analyze_price_elasticity(changes, sales, snapshots)

        # At $14.99, BSR was 500000
        assert price_points[0].avg_bsr == 500000
        # At $4.99, BSR was 100000
        assert price_points[1].avg_bsr == 100000

    def test_elasticity_calculation(self, price_history_db):
        db, book_id = price_history_db
        changes = db.get_price_changes(book_id)
        sales = db.get_sales(book_id)
        snapshots = db.get_snapshots(book_id)

        _, elasticity = analyze_price_elasticity(changes, sales, snapshots)

        assert len(elasticity) == 1
        er = elasticity[0]
        assert er.price_from == 14.99
        assert er.price_to == 4.99
        # Price went down, quantity went up — negative elasticity
        assert er.pct_price_change < 0  # Price decreased
        assert er.pct_quantity_change > 0  # Quantity increased
        assert er.elasticity < 0  # Normal demand curve

    def test_empty_price_changes(self):
        price_points, elasticity = analyze_price_elasticity([], [], [])
        assert price_points == []
        assert elasticity == []

    def test_single_price_change(self, sample_book):
        db, book_id = sample_book
        db.add_price_change(book_id, new_price=4.99, changed_at='2026-01-01')

        changes = db.get_price_changes(book_id)
        price_points, elasticity = analyze_price_elasticity(changes, [], [])

        assert len(price_points) == 1
        assert price_points[0].price == 4.99
        assert elasticity == []  # Can't compute elasticity with one point

    def test_daily_revenue_uses_royalty(self, price_history_db):
        db, book_id = price_history_db
        changes = db.get_price_changes(book_id)
        sales = db.get_sales(book_id)
        snapshots = db.get_snapshots(book_id)

        price_points, _ = analyze_price_elasticity(changes, sales, snapshots)

        # Daily revenue = avg_daily_units * royalty_per_unit
        for pp in price_points:
            expected = round(pp.avg_daily_units * pp.royalty_per_unit, 4)
            assert pp.daily_revenue == expected

    def test_no_sales_data(self, sample_book):
        db, book_id = sample_book
        db.add_price_change(book_id, new_price=4.99, changed_at='2026-01-01')
        db.add_price_change(book_id, new_price=9.99, changed_at='2026-02-01')

        changes = db.get_price_changes(book_id)
        price_points, _ = analyze_price_elasticity(changes, [], [])

        assert len(price_points) == 2
        for pp in price_points:
            assert pp.total_units == 0
            assert pp.daily_revenue == 0.0

    def test_no_snapshots(self, sample_book):
        db, book_id = sample_book
        db.add_price_change(book_id, new_price=4.99, changed_at='2026-01-01')

        changes = db.get_price_changes(book_id)
        price_points, _ = analyze_price_elasticity(changes, [], [])

        assert price_points[0].avg_bsr is None

    def test_elasticity_interpretation_elastic(self):
        """When elasticity > 1, demand is elastic."""
        # Synthetic data: big qty change, small price change
        changes = [
            PriceChange(id=1, book_id=1, new_price=5.00, changed_at='2026-01-01'),
            PriceChange(id=2, book_id=1, new_price=4.50, changed_at='2026-02-01'),
        ]
        # At $5.00: 1 unit/day over 31 days
        sales_1 = [Sale(id=i, book_id=1, date=f'2026-01-{d:02d}', units=1, royalty_amount=3.42)
                    for i, d in enumerate(range(1, 32), start=1)]
        # At $4.50: 3 units/day over 28 days (big increase)
        sales_2 = [Sale(id=i+31, book_id=1, date=f'2026-02-{d:02d}', units=3, royalty_amount=3.08)
                    for i, d in enumerate(range(1, 29), start=1)]

        _, elasticity = analyze_price_elasticity(changes, sales_1 + sales_2, [])
        if elasticity:
            assert 'elastic' in elasticity[0].interpretation.lower()


class TestRecommendPrice:
    """Test price recommendation engine."""

    def test_with_price_history(self, price_history_db):
        db, book_id = price_history_db
        changes = db.get_price_changes(book_id)
        sales = db.get_sales(book_id)
        snapshots = db.get_snapshots(book_id)

        price_points, _ = analyze_price_elasticity(changes, sales, snapshots)
        rec = recommend_price(price_points)

        assert rec.recommended_price is not None
        assert rec.price_points_analyzed == 2
        assert rec.confidence in ('low', 'medium', 'high')

    def test_empty_data(self):
        rec = recommend_price([])
        assert rec.recommended_price is None
        assert 'No price history' in rec.reasoning

    def test_single_price_point(self, sample_book):
        db, book_id = sample_book
        db.add_price_change(book_id, new_price=4.99, changed_at='2026-01-01')

        changes = db.get_price_changes(book_id)
        price_points, _ = analyze_price_elasticity(changes, [], [])
        rec = recommend_price(price_points)

        assert rec.recommended_price == 4.99
        assert rec.confidence == 'low'
        assert 'Only one price point' in rec.reasoning

    def test_picks_highest_revenue(self):
        """Should recommend the price with highest daily revenue."""
        from price_optimizer.models import PricePoint
        points = [
            PricePoint(price=2.99, daily_revenue=1.50, avg_daily_units=1.5,
                       royalty_per_unit=1.00, days_active=14),
            PricePoint(price=4.99, daily_revenue=3.00, avg_daily_units=1.0,
                       royalty_per_unit=3.00, days_active=14),
            PricePoint(price=9.99, daily_revenue=2.00, avg_daily_units=0.3,
                       royalty_per_unit=6.50, days_active=14),
        ]
        rec = recommend_price(points)
        assert rec.recommended_price == 4.99
        assert rec.estimated_daily_revenue == 3.00

    def test_confidence_high_with_good_data(self):
        from price_optimizer.models import PricePoint
        points = [
            PricePoint(price=2.99, daily_revenue=1.50, days_active=14,
                       avg_daily_units=1.0, royalty_per_unit=1.50),
            PricePoint(price=4.99, daily_revenue=3.00, days_active=14,
                       avg_daily_units=1.0, royalty_per_unit=3.00),
            PricePoint(price=9.99, daily_revenue=2.00, days_active=14,
                       avg_daily_units=0.3, royalty_per_unit=6.50),
        ]
        rec = recommend_price(points)
        assert rec.confidence == 'high'

    def test_confidence_low_with_short_data(self):
        from price_optimizer.models import PricePoint
        points = [
            PricePoint(price=2.99, daily_revenue=1.50, days_active=3,
                       avg_daily_units=1.0, royalty_per_unit=1.50),
            PricePoint(price=4.99, daily_revenue=3.00, days_active=5,
                       avg_daily_units=1.0, royalty_per_unit=3.00),
        ]
        rec = recommend_price(points)
        assert rec.confidence == 'low'

    def test_with_kenp_baseline(self, price_history_db):
        db, book_id = price_history_db
        changes = db.get_price_changes(book_id)
        sales = db.get_sales(book_id)
        snapshots = db.get_snapshots(book_id)

        price_points, _ = analyze_price_elasticity(changes, sales, snapshots)
        rec = recommend_price(price_points, kenp_baseline=350, kenp_rate=0.0045)

        # Should still work with KENP data
        assert rec.recommended_price is not None
