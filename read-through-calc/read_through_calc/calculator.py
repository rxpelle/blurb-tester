from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from .models import BookInfo, ReadThroughResult, ReadThroughReport, LTVReport, PricingScenario
from .db import ReadOnlyDB


def calculate_read_through_overall(db: ReadOnlyDB, book1: BookInfo, book2: BookInfo) -> float:
    """Simple overall read-through: total Book 2 units / total Book 1 units. Capped at 1.0."""
    b1_units = db.get_total_units(book1.id)
    b2_units = db.get_total_units(book2.id)
    if b1_units == 0:
        return 0.0
    return min(b2_units / b1_units, 1.0)


def calculate_read_through_cohort(db: ReadOnlyDB, book1: BookInfo, book2: BookInfo,
                                   read_window_days: int = 60) -> Tuple[Optional[float], int]:
    """
    Cohort-based read-through: for each month of Book 1 sales, check how many
    bought Book 2 within the read window.

    Returns (rate, num_periods). Rate is None if no valid cohort periods exist.
    """
    b1_monthly = db.get_monthly_units(book1.id)
    if not b1_monthly:
        return None, 0

    total_b1 = 0
    total_b2_in_window = 0
    valid_periods = 0

    for period in b1_monthly:
        month_str = period['month']
        b1_units = period['units']
        if b1_units <= 0:
            continue

        # Calculate window: from start of this month to end of month + read_window_days
        month_start = datetime.strptime(month_str + '-01', '%Y-%m-%d')
        # End of month: go to next month, subtract a day
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        window_end = month_end + timedelta(days=read_window_days)

        b2_in_window = db.get_units_in_window(
            book2.id,
            month_start.strftime('%Y-%m-%d'),
            window_end.strftime('%Y-%m-%d'),
        )

        total_b1 += b1_units
        total_b2_in_window += b2_in_window
        valid_periods += 1

    if total_b1 == 0 or valid_periods == 0:
        return None, 0

    rate = min(total_b2_in_window / total_b1, 1.0)
    return rate, valid_periods


def calculate_series_read_through(db: ReadOnlyDB, books: List[BookInfo],
                                   read_window_days: int = 60) -> List[ReadThroughResult]:
    """Calculate read-through between each consecutive pair in a series."""
    results = []
    for i in range(len(books) - 1):
        b1 = books[i]
        b2 = books[i + 1]
        b1_units = db.get_total_units(b1.id)
        b2_units = db.get_total_units(b2.id)
        overall = calculate_read_through_overall(db, b1, b2)
        cohort_rate, cohort_periods = calculate_read_through_cohort(
            db, b1, b2, read_window_days
        )
        results.append(ReadThroughResult(
            from_book=b1.title,
            to_book=b2.title,
            from_position=b1.series_position,
            to_position=b2.series_position,
            from_units=b1_units,
            to_units=b2_units,
            overall_rate=overall,
            cohort_rate=cohort_rate,
            cohort_periods=cohort_periods,
        ))
    return results


def build_read_through_report(db: ReadOnlyDB, series_name: str,
                               read_window_days: int = 60) -> ReadThroughReport:
    """Build a complete read-through report for a series."""
    books = db.get_series_books(series_name)
    rates = calculate_series_read_through(db, books, read_window_days)

    # Cumulative rate: product of all read-through rates
    cumulative = 1.0
    for r in rates:
        best_rate = r.cohort_rate if r.cohort_rate is not None else r.overall_rate
        cumulative *= best_rate

    return ReadThroughReport(
        series_name=series_name,
        books=books,
        rates=rates,
        cumulative_rate=cumulative,
    )


def kdp_royalty_rate(price: float) -> float:
    """Return KDP royalty rate based on price tier."""
    if 2.99 <= price <= 9.99:
        return 0.70
    return 0.35


def calculate_royalty(price: float, delivery_cost: float = 0.15) -> float:
    """Calculate per-unit royalty at a given price."""
    rate = kdp_royalty_rate(price)
    if rate == 0.70:
        return round((price - delivery_cost) * rate, 4)
    return round(price * rate, 4)


def calculate_ltv(db: ReadOnlyDB, books: List[BookInfo],
                  read_through_rates: List[float],
                  kenp_rate: float = 0.0045) -> LTVReport:
    """
    Calculate lifetime reader value for a series.

    read_through_rates: list of N-1 rates for transitions between books.
    """
    if not books:
        return LTVReport(series_name='', kenp_rate=kenp_rate)

    series_name = books[0].series_name

    # Build cumulative rates
    cumulative_rates = [1.0]
    for rt in read_through_rates:
        cumulative_rates.append(cumulative_rates[-1] * rt)

    per_book_royalty = []
    per_book_kenp = []
    per_book_ltv = []
    total = 0.0

    for i, book in enumerate(books):
        avg_royalty = db.get_avg_royalty_per_unit(book.id)
        per_book_royalty.append(round(avg_royalty, 4))

        kenp_value = 0.0
        if book.kenp_baseline and book.kenp_baseline > 0:
            kenp_value = book.kenp_baseline * kenp_rate
        per_book_kenp.append(round(kenp_value, 4))

        contribution = (avg_royalty + kenp_value) * cumulative_rates[i]
        per_book_ltv.append(round(contribution, 4))
        total += contribution

    return LTVReport(
        series_name=series_name,
        books=books,
        read_through_rates=read_through_rates,
        cumulative_rates=cumulative_rates,
        per_book_royalty=per_book_royalty,
        per_book_kenp_value=per_book_kenp,
        per_book_ltv_contribution=per_book_ltv,
        total_ltv=round(total, 2),
        kenp_rate=kenp_rate,
    )


def calculate_ltv_from_db(db: ReadOnlyDB, series_name: str,
                           kenp_rate: float = 0.0045,
                           read_window_days: int = 60) -> LTVReport:
    """Calculate LTV pulling read-through rates from actual data."""
    books = db.get_series_books(series_name)
    if len(books) < 2:
        # Single book, no read-through
        return calculate_ltv(db, books, [], kenp_rate)

    rt_results = calculate_series_read_through(db, books, read_window_days)
    rates = []
    for r in rt_results:
        best = r.cohort_rate if r.cohort_rate is not None else r.overall_rate
        rates.append(best)

    return calculate_ltv(db, books, rates, kenp_rate)


def pricing_scenario(db: ReadOnlyDB, books: List[BookInfo],
                     read_through_rates: List[float],
                     prices: List[float],
                     kenp_rate: float = 0.0045) -> PricingScenario:
    """
    Calculate a what-if pricing scenario.

    prices: list of prices, one per book. If shorter than books, remaining use current DB price.
    """
    if not books:
        return PricingScenario(series_name='', kenp_rate=kenp_rate)

    series_name = books[0].series_name

    # Pad prices with current prices from DB
    full_prices = list(prices)
    while len(full_prices) < len(books):
        db_price = db.get_latest_price(books[len(full_prices)].id)
        full_prices.append(db_price or 4.99)

    # Build cumulative rates
    cumulative_rates = [1.0]
    for rt in read_through_rates:
        cumulative_rates.append(cumulative_rates[-1] * rt)

    royalty_rates = []
    per_book_royalty = []
    per_book_ltv = []
    total = 0.0

    for i, book in enumerate(books):
        price = full_prices[i]
        rate = kdp_royalty_rate(price)
        royalty = calculate_royalty(price)
        royalty_rates.append(rate)
        per_book_royalty.append(round(royalty, 4))

        kenp_value = 0.0
        if book.kenp_baseline and book.kenp_baseline > 0:
            kenp_value = book.kenp_baseline * kenp_rate

        contribution = (royalty + kenp_value) * cumulative_rates[i]
        per_book_ltv.append(round(contribution, 4))
        total += contribution

    revenue_per_100 = round(total * 100, 2)

    return PricingScenario(
        series_name=series_name,
        books=books,
        prices=full_prices,
        royalty_rates=royalty_rates,
        per_book_royalty=per_book_royalty,
        read_through_rates=read_through_rates,
        cumulative_rates=cumulative_rates,
        per_book_ltv_contribution=per_book_ltv,
        total_ltv=round(total, 2),
        revenue_per_100=revenue_per_100,
        kenp_rate=kenp_rate,
    )


def pricing_scenario_from_db(db: ReadOnlyDB, series_name: str,
                              prices: List[float],
                              kenp_rate: float = 0.0045,
                              read_window_days: int = 60) -> PricingScenario:
    """Calculate pricing scenario pulling read-through rates from actual data."""
    books = db.get_series_books(series_name)
    if len(books) < 2:
        return pricing_scenario(db, books, [], prices, kenp_rate)

    rt_results = calculate_series_read_through(db, books, read_window_days)
    rates = []
    for r in rt_results:
        best = r.cohort_rate if r.cohort_rate is not None else r.overall_rate
        rates.append(best)

    return pricing_scenario(db, books, rates, prices, kenp_rate)
