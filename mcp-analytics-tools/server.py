"""MCP Analytics Tools Server - Wraps 7 analytics packages for KDP publishing."""

import anyio
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-analytics-tools")

# --- Lazy imports with graceful fallback ---

try:
    from price_optimizer.optimizer import analyze_price_elasticity, recommend_price
except ImportError:
    analyze_price_elasticity = None
    recommend_price = None

try:
    from price_optimizer.royalty_calc import calculate_royalty
except ImportError:
    calculate_royalty = None

try:
    from price_optimizer.experiments import (
        create_experiment,
        get_experiment_status,
    )
except ImportError:
    create_experiment = None
    get_experiment_status = None

try:
    from funnel_analyzer.funnel import get_funnel_report
except ImportError:
    get_funnel_report = None

try:
    from funnel_analyzer.ab_test import compare_magnets
except ImportError:
    compare_magnets = None

try:
    from read_through_calc.calculator import (
        calculate_read_through,
        calculate_ltv,
        pricing_scenario,
    )
except ImportError:
    calculate_read_through = None
    calculate_ltv = None
    pricing_scenario = None

try:
    from ku_page_flip.detector import detect_anomalies
except ImportError:
    detect_anomalies = None

try:
    from ku_page_flip.reporter import import_kenp_csv
except ImportError:
    import_kenp_csv = None

try:
    from royalty_reconciler.parsers import import_royalty_csv
except ImportError:
    import_royalty_csv = None

try:
    from royalty_reconciler.reconciler import generate_pnl
except ImportError:
    generate_pnl = None

try:
    from royalty_reconciler.tax import generate_schedule_c
except ImportError:
    generate_schedule_c = None

try:
    from audiobook_calc.calculator import estimate_production
except ImportError:
    estimate_production = None

try:
    from audiobook_calc.comparator import compare_deals
except ImportError:
    compare_deals = None

try:
    from backmatter_tracker.tracker import create_tracked_link
except ImportError:
    create_tracked_link = None

try:
    from backmatter_tracker.analytics import get_backmatter_report
except ImportError:
    get_backmatter_report = None


def _check(func, package: str):
    """Raise if a required function wasn't imported."""
    if func is None:
        raise RuntimeError(
            f"Package '{package}' is not installed. Install it with: pip install {package}"
        )


# ---------------------------------------------------------------------------
# Price Optimizer tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def analytics_price_history(asin: str) -> str:
    """Show price change history with BSR impact for a given ASIN."""
    _check(analyze_price_elasticity, "price_optimizer")
    result = await anyio.to_thread.run_sync(lambda: analyze_price_elasticity(asin))
    return str(result)


@mcp.tool()
async def analytics_price_recommend(asin: str) -> str:
    """Recommend optimal price for a given ASIN with reasoning."""
    _check(recommend_price, "price_optimizer")
    result = await anyio.to_thread.run_sync(lambda: recommend_price(asin))
    return str(result)


@mcp.tool()
async def analytics_royalty_calc(
    price: float, format: str, marketplace: str = "US"
) -> str:
    """Calculate KDP royalty breakdown. Format: 'ebook' or 'paperback'."""
    _check(calculate_royalty, "price_optimizer")
    result = await anyio.to_thread.run_sync(
        lambda: calculate_royalty(price, format, marketplace)
    )
    return str(result)


@mcp.tool()
async def analytics_price_experiment(
    asin: str, prices: str, duration_days: int = 14
) -> str:
    """Start or check a price experiment. Prices as comma-separated values (e.g. '2.99,3.99,4.99')."""
    _check(create_experiment, "price_optimizer")
    _check(get_experiment_status, "price_optimizer")
    price_list = [float(p.strip()) for p in prices.split(",")]
    result = await anyio.to_thread.run_sync(
        lambda: create_experiment(asin, price_list, duration_days)
    )
    return str(result)


# ---------------------------------------------------------------------------
# Funnel Analyzer tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def analytics_funnel_report(magnet_name: str) -> str:
    """Show funnel visualization with drop-off rates for a reader magnet."""
    _check(get_funnel_report, "funnel_analyzer")
    result = await anyio.to_thread.run_sync(lambda: get_funnel_report(magnet_name))
    return str(result)


@mcp.tool()
async def analytics_funnel_compare(magnet_a: str, magnet_b: str) -> str:
    """Compare two reader magnets side-by-side."""
    _check(compare_magnets, "funnel_analyzer")
    result = await anyio.to_thread.run_sync(lambda: compare_magnets(magnet_a, magnet_b))
    return str(result)


# ---------------------------------------------------------------------------
# Read-Through Calculator tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def analytics_read_through(series_name: str) -> str:
    """Full read-through analysis showing rates per book in a series."""
    _check(calculate_read_through, "read_through_calc")
    result = await anyio.to_thread.run_sync(
        lambda: calculate_read_through(series_name)
    )
    return str(result)


@mcp.tool()
async def analytics_ltv(series_name: str) -> str:
    """Calculate lifetime reader value for a series."""
    _check(calculate_ltv, "read_through_calc")
    result = await anyio.to_thread.run_sync(lambda: calculate_ltv(series_name))
    return str(result)


@mcp.tool()
async def analytics_pricing_scenario(series_name: str, prices: str) -> str:
    """What-if pricing scenario. Prices as comma-separated per book (e.g. '0.99,4.99,4.99')."""
    _check(pricing_scenario, "read_through_calc")
    price_list = [float(p.strip()) for p in prices.split(",")]
    result = await anyio.to_thread.run_sync(
        lambda: pricing_scenario(series_name, price_list)
    )
    return str(result)


# ---------------------------------------------------------------------------
# KU Page Flip / KENP tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def analytics_kenp_analyze(asin: str) -> str:
    """Detect KENP read anomalies (page-flip fraud, unusual patterns) for an ASIN."""
    _check(detect_anomalies, "ku_page_flip")
    result = await anyio.to_thread.run_sync(lambda: detect_anomalies(asin))
    return str(result)


@mcp.tool()
async def analytics_kenp_import(csv_path: str, asin: str) -> str:
    """Import KENP data from a CSV file for an ASIN."""
    _check(import_kenp_csv, "ku_page_flip")
    result = await anyio.to_thread.run_sync(lambda: import_kenp_csv(csv_path, asin))
    return str(result)


# ---------------------------------------------------------------------------
# Royalty Reconciler tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def analytics_royalty_import(csv_path: str, platform: str = "kdp") -> str:
    """Import royalty CSV from a platform (kdp, acx, ingramspark, etc.)."""
    _check(import_royalty_csv, "royalty_reconciler")
    result = await anyio.to_thread.run_sync(
        lambda: import_royalty_csv(csv_path, platform)
    )
    return str(result)


@mcp.tool()
async def analytics_pnl(
    period: str = "month", start_date: str = "", end_date: str = ""
) -> str:
    """Generate profit & loss report. Period: 'month' or 'year'."""
    _check(generate_pnl, "royalty_reconciler")
    result = await anyio.to_thread.run_sync(
        lambda: generate_pnl(period, start_date, end_date)
    )
    return str(result)


@mcp.tool()
async def analytics_tax_report(year: int) -> str:
    """Generate Schedule C tax report for a given year."""
    _check(generate_schedule_c, "royalty_reconciler")
    result = await anyio.to_thread.run_sync(lambda: generate_schedule_c(year))
    return str(result)


# ---------------------------------------------------------------------------
# Audiobook Calculator tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def analytics_audiobook_estimate(word_count: int) -> str:
    """Estimate audiobook production cost and finished length from word count."""
    _check(estimate_production, "audiobook_calc")
    result = await anyio.to_thread.run_sync(lambda: estimate_production(word_count))
    return str(result)


@mcp.tool()
async def analytics_audiobook_compare_deals(
    word_count: int, upfront_cost: float = 0.0, royalty_rate: float = 0.0
) -> str:
    """Compare audiobook deal structures (royalty share vs PFH vs hybrid)."""
    _check(compare_deals, "audiobook_calc")
    result = await anyio.to_thread.run_sync(
        lambda: compare_deals(word_count, upfront_cost, royalty_rate)
    )
    return str(result)


# ---------------------------------------------------------------------------
# Backmatter Tracker tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def analytics_backmatter_create(
    book_title: str, cta_text: str, destination_url: str
) -> str:
    """Create a tracked backmatter link with UTM parameters."""
    _check(create_tracked_link, "backmatter_tracker")
    result = await anyio.to_thread.run_sync(
        lambda: create_tracked_link(book_title, cta_text, destination_url)
    )
    return str(result)


@mcp.tool()
async def analytics_backmatter_report(book_title: str) -> str:
    """Show backmatter link performance with click-through rates."""
    _check(get_backmatter_report, "backmatter_tracker")
    result = await anyio.to_thread.run_sync(
        lambda: get_backmatter_report(book_title)
    )
    return str(result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
