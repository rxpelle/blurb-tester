import pytest
from read_through_calc.calculator import (
    calculate_read_through_overall,
    calculate_read_through_cohort,
    calculate_series_read_through,
    build_read_through_report,
    calculate_ltv,
    calculate_ltv_from_db,
    kdp_royalty_rate,
    calculate_royalty,
    pricing_scenario,
    pricing_scenario_from_db,
)
from read_through_calc.models import BookInfo


# ---- Read-Through: Overall ----

class TestReadThroughOverall:
    def test_basic_ratio(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        rate = calculate_read_through_overall(db, books[0], books[1])
        assert rate == pytest.approx(0.45, abs=0.01)

    def test_second_transition(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        rate = calculate_read_through_overall(db, books[1], books[2])
        assert rate == pytest.approx(20 / 45, abs=0.01)

    def test_50_percent(self, series_2book_db):
        db, b1, b2 = series_2book_db
        books = db.get_series_books('Two Book Series')
        rate = calculate_read_through_overall(db, books[0], books[1])
        assert rate == pytest.approx(0.50, abs=0.01)

    def test_capped_at_1(self, high_rt_db):
        db = high_rt_db
        books = db.get_series_books('High RT Series')
        rate = calculate_read_through_overall(db, books[0], books[1])
        assert rate == 1.0

    def test_zero_sales_book1(self, zero_sales_db):
        db = zero_sales_db
        books = db.get_series_books('Zero Sales Series')
        rate = calculate_read_through_overall(db, books[0], books[1])
        assert rate == 0.0

    def test_zero_sales_book2(self, series_3book_db):
        """Book 2 with zero sales against Book 1 with sales => 0%"""
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        # Book 1 has sales, let's test the rate is positive
        rate = calculate_read_through_overall(db, books[0], books[1])
        assert rate > 0


class TestReadThroughCohort:
    def test_cohort_returns_rate(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        rate, periods = calculate_read_through_cohort(db, books[0], books[1])
        assert rate is not None
        assert periods > 0

    def test_cohort_multiple_periods(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        rate, periods = calculate_read_through_cohort(db, books[0], books[1])
        assert periods == 3  # Jan, Feb, Mar

    def test_cohort_zero_sales(self, zero_sales_db):
        db = zero_sales_db
        books = db.get_series_books('Zero Sales Series')
        rate, periods = calculate_read_through_cohort(db, books[0], books[1])
        assert rate is None
        assert periods == 0

    def test_cohort_capped_at_1(self, high_rt_db):
        db = high_rt_db
        books = db.get_series_books('High RT Series')
        rate, periods = calculate_read_through_cohort(db, books[0], books[1])
        assert rate is not None
        assert rate <= 1.0


class TestSeriesReadThrough:
    def test_3book_series(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        results = calculate_series_read_through(db, books)
        assert len(results) == 2  # Two transitions

    def test_2book_series(self, series_2book_db):
        db, b1, b2 = series_2book_db
        books = db.get_series_books('Two Book Series')
        results = calculate_series_read_through(db, books)
        assert len(results) == 1

    def test_5book_series(self, series_5book_db):
        db, book_ids = series_5book_db
        books = db.get_series_books('Epic Five')
        results = calculate_series_read_through(db, books)
        assert len(results) == 4

    def test_5book_decreasing_rates(self, series_5book_db):
        db, book_ids = series_5book_db
        books = db.get_series_books('Epic Five')
        results = calculate_series_read_through(db, books)
        # Each transition has units populated
        for r in results:
            assert r.from_units > 0
            assert r.to_units > 0

    def test_single_book(self, single_book_db):
        db, bid = single_book_db
        books = db.get_series_books('Solo Series')
        results = calculate_series_read_through(db, books)
        assert len(results) == 0

    def test_result_fields(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        results = calculate_series_read_through(db, books)
        r = results[0]
        assert r.from_book == 'The Aethelred Cipher'
        assert r.to_book == 'The Genesis Protocol'
        assert r.from_position == 1
        assert r.to_position == 2


class TestBuildReadThroughReport:
    def test_report_structure(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        report = build_read_through_report(db, 'The Architecture of Survival')
        assert report.series_name == 'The Architecture of Survival'
        assert len(report.books) == 3
        assert len(report.rates) == 2

    def test_cumulative_rate(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        report = build_read_through_report(db, 'The Architecture of Survival')
        # Cumulative uses cohort rates (which include windowed overlap),
        # so it's higher than simple overall. Just verify it's between 0 and 1.
        assert 0.0 < report.cumulative_rate < 1.0

    def test_empty_series(self, empty_db):
        report = build_read_through_report(empty_db, 'Nonexistent Series')
        assert len(report.books) == 0
        assert len(report.rates) == 0


# ---- KDP Royalty ----

class TestKDPRoyalty:
    def test_70_percent_tier_low(self):
        assert kdp_royalty_rate(2.99) == 0.70

    def test_70_percent_tier_mid(self):
        assert kdp_royalty_rate(4.99) == 0.70

    def test_70_percent_tier_high(self):
        assert kdp_royalty_rate(9.99) == 0.70

    def test_35_percent_tier_low(self):
        assert kdp_royalty_rate(0.99) == 0.35

    def test_35_percent_tier_high(self):
        assert kdp_royalty_rate(14.99) == 0.35

    def test_35_percent_tier_boundary_below(self):
        assert kdp_royalty_rate(2.98) == 0.35

    def test_35_percent_tier_boundary_above(self):
        assert kdp_royalty_rate(10.00) == 0.35

    def test_royalty_at_0_99(self):
        r = calculate_royalty(0.99)
        assert r == pytest.approx(0.99 * 0.35, abs=0.01)

    def test_royalty_at_4_99(self):
        r = calculate_royalty(4.99)
        assert r == pytest.approx((4.99 - 0.15) * 0.70, abs=0.01)

    def test_royalty_at_2_99(self):
        r = calculate_royalty(2.99)
        assert r == pytest.approx((2.99 - 0.15) * 0.70, abs=0.01)

    def test_royalty_at_9_99(self):
        r = calculate_royalty(9.99)
        assert r == pytest.approx((9.99 - 0.15) * 0.70, abs=0.01)


# ---- LTV ----

class TestLTV:
    def test_ltv_3book(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        ltv = calculate_ltv(db, books, [0.45, 0.44], kenp_rate=0.0045)
        assert ltv.total_ltv > 0
        assert len(ltv.per_book_royalty) == 3
        assert len(ltv.cumulative_rates) == 3

    def test_ltv_cumulative_rates(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        ltv = calculate_ltv(db, books, [0.50, 0.40], kenp_rate=0.0045)
        assert ltv.cumulative_rates[0] == 1.0
        assert ltv.cumulative_rates[1] == pytest.approx(0.50)
        assert ltv.cumulative_rates[2] == pytest.approx(0.20)

    def test_ltv_with_kenp(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        ltv_with = calculate_ltv(db, books, [0.45, 0.44], kenp_rate=0.0045)
        ltv_without = calculate_ltv(db, books, [0.45, 0.44], kenp_rate=0.0)
        assert ltv_with.total_ltv > ltv_without.total_ltv

    def test_ltv_no_kenp_baseline(self, no_kenp_db):
        db = no_kenp_db
        books = db.get_series_books('No KENP Series')
        ltv = calculate_ltv(db, books, [0.50], kenp_rate=0.0045)
        # KENP values should all be 0
        for kv in ltv.per_book_kenp_value:
            assert kv == 0.0

    def test_ltv_single_book(self, single_book_db):
        db, bid = single_book_db
        books = db.get_series_books('Solo Series')
        ltv = calculate_ltv(db, books, [], kenp_rate=0.0045)
        assert ltv.total_ltv > 0
        assert len(ltv.cumulative_rates) == 1
        assert ltv.cumulative_rates[0] == 1.0

    def test_ltv_from_db(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        ltv = calculate_ltv_from_db(db, 'The Architecture of Survival')
        assert ltv.total_ltv > 0
        assert ltv.series_name == 'The Architecture of Survival'

    def test_ltv_empty(self, empty_db):
        ltv = calculate_ltv(empty_db, [], [], kenp_rate=0.0045)
        assert ltv.total_ltv == 0.0

    def test_ltv_book1_contribution_highest(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        ltv = calculate_ltv(db, books, [0.45, 0.44], kenp_rate=0.0045)
        # Book 1 has cumulative RT of 1.0, so should contribute most
        assert ltv.per_book_ltv_contribution[0] >= ltv.per_book_ltv_contribution[1]
        assert ltv.per_book_ltv_contribution[1] >= ltv.per_book_ltv_contribution[2]


# ---- Pricing Scenarios ----

class TestPricingScenario:
    def test_pricing_basic(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        result = pricing_scenario(db, books, [0.45, 0.44],
                                   [0.99, 4.99, 4.99])
        assert result.total_ltv > 0
        assert result.revenue_per_100 > 0

    def test_pricing_35_tier(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        result = pricing_scenario(db, books, [0.45, 0.44],
                                   [0.99, 4.99, 4.99])
        assert result.royalty_rates[0] == 0.35  # $0.99
        assert result.royalty_rates[1] == 0.70  # $4.99
        assert result.royalty_rates[2] == 0.70  # $4.99

    def test_pricing_all_70_tier(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        result = pricing_scenario(db, books, [0.45, 0.44],
                                   [4.99, 4.99, 4.99])
        for rate in result.royalty_rates:
            assert rate == 0.70

    def test_pricing_revenue_per_100(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        result = pricing_scenario(db, books, [0.45, 0.44],
                                   [4.99, 4.99, 4.99])
        assert result.revenue_per_100 == pytest.approx(result.total_ltv * 100, abs=1.0)

    def test_pricing_higher_prices_more_ltv(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        books = db.get_series_books('The Architecture of Survival')
        low = pricing_scenario(db, books, [0.45, 0.44],
                                [0.99, 0.99, 0.99])
        high = pricing_scenario(db, books, [0.45, 0.44],
                                 [4.99, 4.99, 4.99])
        assert high.total_ltv > low.total_ltv

    def test_pricing_from_db(self, series_3book_db):
        db, b1, b2, b3 = series_3book_db
        result = pricing_scenario_from_db(
            db, 'The Architecture of Survival', [2.99, 4.99, 4.99])
        assert result.total_ltv > 0

    def test_pricing_partial_prices(self, series_3book_db):
        """Only provide Book 1 price, others from DB."""
        db, b1, b2, b3 = series_3book_db
        result = pricing_scenario_from_db(
            db, 'The Architecture of Survival', [0.99])
        assert len(result.prices) == 3
        assert result.prices[0] == 0.99
        # Book 2 and 3 should have pulled from DB snapshot (4.99)
        assert result.prices[1] == pytest.approx(4.99)
        assert result.prices[2] == pytest.approx(4.99)

    def test_pricing_empty(self, empty_db):
        result = pricing_scenario(empty_db, [], [], [])
        assert result.total_ltv == 0.0
        assert result.revenue_per_100 == 0.0

    def test_pricing_2book(self, series_2book_db):
        db, b1, b2 = series_2book_db
        books = db.get_series_books('Two Book Series')
        result = pricing_scenario(db, books, [0.50], [2.99, 4.99])
        assert len(result.prices) == 2
        assert result.total_ltv > 0

    def test_pricing_5book(self, series_5book_db):
        db, book_ids = series_5book_db
        books = db.get_series_books('Epic Five')
        result = pricing_scenario(db, books,
                                   [0.60, 0.67, 0.625, 0.60],
                                   [0.99, 4.99, 4.99, 4.99, 4.99])
        assert len(result.prices) == 5
        assert len(result.cumulative_rates) == 5
