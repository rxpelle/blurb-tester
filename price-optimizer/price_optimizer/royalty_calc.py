"""KDP royalty calculator encoding actual Amazon royalty rules.

CRITICAL: Authors use this for financial decisions. Must be accurate.
"""

from .models import RoyaltyResult


# 70% royalty tier price bounds by marketplace (in local currency)
SEVENTY_PCT_BOUNDS = {
    'US': (2.99, 9.99, 'USD'),
    'CA': (2.99, 9.99, 'CAD'),
    'UK': (1.99, 6.99, 'GBP'),
    'DE': (2.99, 9.99, 'EUR'),
    'FR': (2.99, 9.99, 'EUR'),
    'ES': (2.99, 9.99, 'EUR'),
    'IT': (2.99, 9.99, 'EUR'),
    'NL': (2.99, 9.99, 'EUR'),
    'JP': (250, 1250, 'JPY'),
    'BR': (5.99, 24.99, 'BRL'),
    'MX': (34.99, 174.99, 'MXN'),
    'AU': (3.99, 13.99, 'AUD'),
    'IN': (49, 199, 'INR'),
}

# Marketplaces that support 70% royalty
SEVENTY_PCT_MARKETPLACES = set(SEVENTY_PCT_BOUNDS.keys())

# Paperback printing costs per page (approximate, US marketplace)
PAPERBACK_BW_PER_PAGE = 0.012
PAPERBACK_COLOR_PER_PAGE = 0.07
PAPERBACK_FIXED_COST = 0.85

# Hardcover printing costs
HARDCOVER_BW_PER_PAGE = 0.012
HARDCOVER_COLOR_PER_PAGE = 0.07
HARDCOVER_FIXED_COST = 6.50

# Delivery cost per MB for 70% ebook tier
DELIVERY_COST_PER_MB = 0.15


def calculate_royalty(price, format='ebook', marketplace='US',
                      page_count=None, print_cost=None, delivery_mb=0.5,
                      color=False):
    """Calculate KDP royalty for a given price and format.

    Args:
        price: List price in local currency
        format: 'ebook', 'paperback', or 'hardcover'
        marketplace: Two-letter marketplace code (US, UK, DE, etc.)
        page_count: Number of pages (for paperback/hardcover cost estimation)
        print_cost: Explicit printing cost (overrides page_count calculation)
        delivery_mb: eBook file size in MB (for 70% tier delivery cost)
        color: Whether interior is color (for print cost estimation)

    Returns:
        RoyaltyResult with royalty_amount, royalty_rate, tier, costs
    """
    if price is None or price < 0:
        return RoyaltyResult(
            price=price if price is not None else 0,
            format=format,
            marketplace=marketplace,
            royalty_amount=0.0,
            royalty_rate=0.0,
            tier='invalid',
        )

    if price == 0:
        return RoyaltyResult(
            price=0.0,
            format=format,
            marketplace=marketplace,
            royalty_amount=0.0,
            royalty_rate=0.0,
            tier='free',
        )

    format_lower = format.lower()

    if format_lower == 'ebook':
        return _calc_ebook_royalty(price, marketplace, delivery_mb)
    elif format_lower == 'paperback':
        return _calc_paperback_royalty(price, marketplace, page_count, print_cost, color)
    elif format_lower == 'hardcover':
        return _calc_hardcover_royalty(price, marketplace, page_count, print_cost, color)
    else:
        # Default to ebook
        return _calc_ebook_royalty(price, marketplace, delivery_mb)


def _calc_ebook_royalty(price, marketplace, delivery_mb):
    """Calculate ebook royalty with 70%/35% tier logic."""
    marketplace = marketplace.upper()

    # Check if 70% tier is available and price qualifies
    can_use_70 = False
    if marketplace in SEVENTY_PCT_BOUNDS:
        min_price, max_price, _currency = SEVENTY_PCT_BOUNDS[marketplace]
        if min_price <= price <= max_price:
            can_use_70 = True

    if can_use_70:
        delivery_cost = delivery_mb * DELIVERY_COST_PER_MB
        royalty = (price * 0.70) - delivery_cost
        # Royalty cannot be negative
        royalty = max(0.0, royalty)
        return RoyaltyResult(
            price=price,
            format='ebook',
            marketplace=marketplace,
            royalty_amount=round(royalty, 2),
            royalty_rate=0.70,
            tier='70%',
            delivery_cost=round(delivery_cost, 2),
        )
    else:
        royalty = price * 0.35
        return RoyaltyResult(
            price=price,
            format='ebook',
            marketplace=marketplace,
            royalty_amount=round(royalty, 2),
            royalty_rate=0.35,
            tier='35%',
            delivery_cost=0.0,
        )


def _estimate_print_cost(page_count, fixed_cost, per_page_bw, per_page_color, color):
    """Estimate printing cost from page count."""
    if page_count is None:
        return None
    per_page = per_page_color if color else per_page_bw
    return round(fixed_cost + (page_count * per_page), 2)


def _calc_paperback_royalty(price, marketplace, page_count, print_cost, color):
    """Paperback: Royalty = 60% x (list price - printing cost)."""
    if print_cost is None:
        print_cost = _estimate_print_cost(
            page_count, PAPERBACK_FIXED_COST,
            PAPERBACK_BW_PER_PAGE, PAPERBACK_COLOR_PER_PAGE, color
        )

    if print_cost is None:
        # Can't calculate without cost info
        return RoyaltyResult(
            price=price,
            format='paperback',
            marketplace=marketplace,
            royalty_amount=0.0,
            royalty_rate=0.60,
            tier='paperback',
            print_cost=0.0,
        )

    royalty = 0.60 * (price - print_cost)
    royalty = max(0.0, royalty)

    return RoyaltyResult(
        price=price,
        format='paperback',
        marketplace=marketplace,
        royalty_amount=round(royalty, 2),
        royalty_rate=0.60,
        tier='paperback',
        print_cost=print_cost,
    )


def _calc_hardcover_royalty(price, marketplace, page_count, print_cost, color):
    """Hardcover: Royalty = 40% x (list price - printing cost)."""
    if print_cost is None:
        print_cost = _estimate_print_cost(
            page_count, HARDCOVER_FIXED_COST,
            HARDCOVER_BW_PER_PAGE, HARDCOVER_COLOR_PER_PAGE, color
        )

    if print_cost is None:
        return RoyaltyResult(
            price=price,
            format='hardcover',
            marketplace=marketplace,
            royalty_amount=0.0,
            royalty_rate=0.40,
            tier='hardcover',
            print_cost=0.0,
        )

    royalty = 0.40 * (price - print_cost)
    royalty = max(0.0, royalty)

    return RoyaltyResult(
        price=price,
        format='hardcover',
        marketplace=marketplace,
        royalty_amount=round(royalty, 2),
        royalty_rate=0.40,
        tier='hardcover',
        print_cost=print_cost,
    )


def calculate_all_tiers(price, delivery_mb=0.5):
    """Calculate royalty at both 35% and 70% tiers for comparison.

    Returns dict with '35%' and '70%' keys.
    """
    result_35 = RoyaltyResult(
        price=price, format='ebook', marketplace='US',
        royalty_amount=round(price * 0.35, 2),
        royalty_rate=0.35, tier='35%',
    )

    delivery_cost = delivery_mb * DELIVERY_COST_PER_MB
    royalty_70 = max(0.0, (price * 0.70) - delivery_cost)
    result_70 = RoyaltyResult(
        price=price, format='ebook', marketplace='US',
        royalty_amount=round(royalty_70, 2),
        royalty_rate=0.70, tier='70%',
        delivery_cost=round(delivery_cost, 2),
    )

    return {'35%': result_35, '70%': result_70}
