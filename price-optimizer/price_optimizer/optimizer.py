"""Core price optimization logic: elasticity analysis and revenue optimization."""

from datetime import datetime, timedelta
from typing import List, Optional
from .models import PricePoint, ElasticityResult, Recommendation
from .royalty_calc import calculate_royalty


def analyze_price_elasticity(price_changes, sales, snapshots):
    """Analyze revenue and BSR at each historical price point.

    For each price point in history:
    1. Find the date range it was active
    2. Get average daily units sold during that period
    3. Get average BSR during that period
    4. Calculate daily revenue = units * royalty_at_price
    5. Price elasticity = (% change in quantity) / (% change in price)

    Args:
        price_changes: List of PriceChange objects, sorted by changed_at ASC
        sales: List of Sale objects covering the full period
        snapshots: List of Snapshot objects covering the full period

    Returns:
        Tuple of (list of PricePoint, list of ElasticityResult)
    """
    if not price_changes:
        return [], []

    price_points = []

    for i, pc in enumerate(price_changes):
        start_date = pc.changed_at[:10]  # Extract date part

        # End date is the next price change, or today
        if i + 1 < len(price_changes):
            end_date = price_changes[i + 1].changed_at[:10]
        else:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # Calculate days active
        try:
            d_start = datetime.strptime(start_date, '%Y-%m-%d')
            d_end = datetime.strptime(end_date, '%Y-%m-%d')
            days_active = max(1, (d_end - d_start).days)
        except ValueError:
            days_active = 1

        # Filter sales in this date range
        period_sales = [s for s in sales if start_date <= s.date <= end_date]
        total_units = sum(s.units for s in period_sales)
        avg_daily_units = total_units / days_active if days_active > 0 else 0

        # Filter snapshots in this date range
        period_snapshots = [s for s in snapshots
                           if s.timestamp and start_date <= s.timestamp[:10] <= end_date]
        bsr_values = [s.bsr for s in period_snapshots if s.bsr is not None]
        avg_bsr = sum(bsr_values) / len(bsr_values) if bsr_values else None

        # Calculate royalty at this price
        royalty = calculate_royalty(pc.new_price)
        royalty_per_unit = royalty.royalty_amount
        daily_revenue = avg_daily_units * royalty_per_unit

        price_points.append(PricePoint(
            price=pc.new_price,
            days_active=days_active,
            total_units=total_units,
            avg_daily_units=round(avg_daily_units, 4),
            avg_bsr=round(avg_bsr, 0) if avg_bsr else None,
            daily_revenue=round(daily_revenue, 4),
            royalty_per_unit=royalty_per_unit,
            start_date=start_date,
            end_date=end_date,
        ))

    # Calculate elasticity between consecutive price points
    elasticity_results = []
    for i in range(1, len(price_points)):
        prev = price_points[i - 1]
        curr = price_points[i]

        if prev.price == 0 or prev.avg_daily_units == 0:
            continue

        pct_price_change = (curr.price - prev.price) / prev.price
        pct_qty_change = ((curr.avg_daily_units - prev.avg_daily_units)
                          / prev.avg_daily_units) if prev.avg_daily_units > 0 else 0

        if pct_price_change == 0:
            continue

        elasticity = pct_qty_change / pct_price_change

        # Interpret
        abs_e = abs(elasticity)
        if abs_e > 1:
            interpretation = 'elastic (demand sensitive to price)'
        elif abs_e == 1:
            interpretation = 'unit elastic'
        else:
            interpretation = 'inelastic (demand not very sensitive to price)'

        elasticity_results.append(ElasticityResult(
            price_from=prev.price,
            price_to=curr.price,
            pct_price_change=round(pct_price_change * 100, 1),
            pct_quantity_change=round(pct_qty_change * 100, 1),
            elasticity=round(elasticity, 2),
            interpretation=interpretation,
        ))

    return price_points, elasticity_results


def recommend_price(price_points, kenp_baseline=None, kenp_rate=0.0045):
    """Find the price that maximizes total daily revenue (sales + KU).

    Args:
        price_points: List of PricePoint from analyze_price_elasticity
        kenp_baseline: Book's KENP page count (for KU revenue estimation)
        kenp_rate: Estimated payment per KENP page read (default ~$0.0045)

    Returns:
        Recommendation dataclass
    """
    if not price_points:
        return Recommendation(
            reasoning='No price history available. Log price changes to get recommendations.',
            price_points_analyzed=0,
        )

    if len(price_points) < 2:
        pp = price_points[0]
        return Recommendation(
            recommended_price=pp.price,
            estimated_daily_revenue=pp.daily_revenue,
            estimated_daily_units=pp.avg_daily_units,
            estimated_royalty=pp.royalty_per_unit,
            confidence='low',
            reasoning=f'Only one price point (${pp.price:.2f}) in history. '
                      f'Need at least 2 price changes to compare performance. '
                      f'Try running a price experiment.',
            price_points_analyzed=1,
        )

    # Score each price point by total daily revenue
    best = None
    best_total_revenue = -1

    for pp in price_points:
        total_revenue = pp.daily_revenue

        # Add estimated KU revenue if KENP data available
        if kenp_baseline and kenp_rate:
            # Rough estimate: KU reads are somewhat independent of price
            # but we don't have per-price-point KENP data, so skip for now
            pass

        if total_revenue > best_total_revenue:
            best_total_revenue = total_revenue
            best = pp

    # Determine confidence based on data quality
    min_days = min(pp.days_active for pp in price_points)
    if min_days >= 14 and len(price_points) >= 3:
        confidence = 'high'
    elif min_days >= 7 and len(price_points) >= 2:
        confidence = 'medium'
    else:
        confidence = 'low'

    # Build reasoning
    prices_str = ', '.join(f'${pp.price:.2f}' for pp in price_points)
    reasoning = (
        f'Analyzed {len(price_points)} price points ({prices_str}). '
        f'${best.price:.2f} generated the highest daily revenue '
        f'(${best.daily_revenue:.2f}/day, {best.avg_daily_units:.1f} units/day). '
    )

    if confidence == 'low':
        reasoning += 'Low confidence — some price points had fewer than 7 days of data.'

    return Recommendation(
        recommended_price=best.price,
        estimated_daily_revenue=best.daily_revenue,
        estimated_daily_units=best.avg_daily_units,
        estimated_royalty=best.royalty_per_unit,
        confidence=confidence,
        reasoning=reasoning,
        price_points_analyzed=len(price_points),
    )
