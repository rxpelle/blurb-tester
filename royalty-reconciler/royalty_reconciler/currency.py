import logging
from datetime import datetime, timedelta
from xml.etree import ElementTree
from typing import Optional

logger = logging.getLogger(__name__)

# Static fallback rates (USD per 1 unit of foreign currency)
STATIC_RATES_TO_USD = {
    'USD': 1.0,
    'GBP': 1.27,
    'EUR': 1.08,
    'CAD': 0.74,
    'AUD': 0.65,
    'JPY': 0.0067,
    'INR': 0.012,
    'BRL': 0.20,
    'MXN': 0.058,
    'SEK': 0.095,
    'DKK': 0.145,
    'NOK': 0.094,
    'PLN': 0.25,
    'CHF': 1.12,
    'NZD': 0.61,
    'SGD': 0.74,
    'HKD': 0.128,
    'ZAR': 0.055,
    'KRW': 0.00075,
    'CNY': 0.14,
    'TWD': 0.031,
    'THB': 0.028,
    'PHP': 0.018,
    'MYR': 0.22,
    'IDR': 0.000063,
    'CZK': 0.044,
    'HUF': 0.0027,
    'ILS': 0.27,
    'CLP': 0.0011,
    'ARS': 0.0011,
    'COP': 0.00025,
    'PEN': 0.27,
    'TRY': 0.031,
    'SAR': 0.27,
    'AED': 0.27,
    'EGP': 0.032,
    'NGN': 0.00065,
    'KES': 0.0077,
    'GHS': 0.066,
}

# ECB rates are EUR-based. Cache parsed rates in memory.
_ecb_cache: dict = {}
_ecb_loaded: bool = False

ECB_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml'
ECB_NS = {'ecb': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}


def _load_ecb_rates() -> bool:
    """Load ECB historical rates into cache. Returns True on success."""
    global _ecb_cache, _ecb_loaded
    if _ecb_loaded:
        return bool(_ecb_cache)
    try:
        import requests
        resp = requests.get(ECB_URL, timeout=10)
        resp.raise_for_status()
        root = ElementTree.fromstring(resp.content)

        for cube_time in root.findall('.//ecb:Cube[@time]', ECB_NS):
            date_str = cube_time.attrib['time']
            rates = {'EUR': 1.0}
            for cube_rate in cube_time.findall('ecb:Cube', ECB_NS):
                currency = cube_rate.attrib.get('currency', '')
                rate = float(cube_rate.attrib.get('rate', 0))
                if currency and rate > 0:
                    rates[currency] = rate
            _ecb_cache[date_str] = rates

        _ecb_loaded = True
        logger.info(f"Loaded ECB rates for {len(_ecb_cache)} dates")
        return True
    except Exception as e:
        logger.warning(f"Could not load ECB rates: {e}")
        _ecb_loaded = True  # Don't retry
        return False


def _find_nearest_ecb_date(date_str: str) -> Optional[str]:
    """Find the nearest available ECB date to the given date."""
    if not _ecb_cache:
        return None
    if date_str in _ecb_cache:
        return date_str
    try:
        target = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None
    # Search within 7 days backward
    for i in range(1, 8):
        candidate = (target - timedelta(days=i)).strftime('%Y-%m-%d')
        if candidate in _ecb_cache:
            return candidate
    # If nothing found, use the most recent date
    dates = sorted(_ecb_cache.keys(), reverse=True)
    return dates[0] if dates else None


def get_exchange_rate(from_currency: str, to_currency: str,
                      date: str = None) -> float:
    """Get exchange rate from one currency to another.

    Args:
        from_currency: Source currency code (e.g., 'GBP')
        to_currency: Target currency code (e.g., 'USD')
        date: Optional date string 'YYYY-MM-DD' for historical rate

    Returns:
        Exchange rate (multiply from_currency amount by this to get to_currency amount)
    """
    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()

    if from_currency == to_currency:
        return 1.0

    # Try ECB rates first
    _load_ecb_rates()

    if _ecb_cache and date:
        ecb_date = _find_nearest_ecb_date(date)
        if ecb_date and ecb_date in _ecb_cache:
            rates = _ecb_cache[ecb_date]
            # ECB rates are EUR-based (EUR/X = rate means 1 EUR = rate X)
            from_eur = rates.get(from_currency)
            to_eur = rates.get(to_currency)
            if from_eur is not None and to_eur is not None:
                # from_currency -> EUR -> to_currency
                return to_eur / from_eur

    # Fallback to static rates via USD
    from_to_usd = STATIC_RATES_TO_USD.get(from_currency)
    to_to_usd = STATIC_RATES_TO_USD.get(to_currency)

    if from_to_usd is None:
        logger.warning(f"Unknown currency: {from_currency}, using 1.0")
        return 1.0
    if to_to_usd is None:
        logger.warning(f"Unknown currency: {to_currency}, using 1.0")
        return 1.0

    # from_currency -> USD -> to_currency
    # from_to_usd = USD per 1 from_currency
    # to_to_usd = USD per 1 to_currency
    # We want: how many to_currency per 1 from_currency
    return from_to_usd / to_to_usd


def convert_to_usd(amount: float, currency: str, date: str = None) -> float:
    """Convert an amount to USD."""
    if currency.upper().strip() == 'USD':
        return amount
    rate = get_exchange_rate(currency, 'USD', date)
    return round(amount * rate, 2)
