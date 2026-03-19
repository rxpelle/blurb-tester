import logging
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)


class ParseError(Exception):
    pass


PLATFORM_PARSERS = {
    'kdp': 'royalty_reconciler.parsers.kdp',
    'apple': 'royalty_reconciler.parsers.apple',
    'kobo': 'royalty_reconciler.parsers.kobo',
    'google': 'royalty_reconciler.parsers.google',
    'd2d': 'royalty_reconciler.parsers.d2d',
    'acx': 'royalty_reconciler.parsers.acx',
}

SUPPORTED_PLATFORMS = list(PLATFORM_PARSERS.keys())


def detect_platform(filepath: str) -> str:
    """Try to auto-detect the platform from CSV headers."""
    from pathlib import Path
    import csv
    from io import StringIO

    path = Path(filepath)
    content = path.read_text(encoding='utf-8-sig')
    reader = csv.reader(StringIO(content))
    try:
        headers = next(reader)
    except StopIteration:
        return 'unknown'

    headers_lower = [h.lower().strip() for h in headers]
    joined = ' '.join(headers_lower)

    if 'asin' in joined or 'royalty type' in joined:
        return 'kdp'
    if 'vendor identifier' in joined or 'product type identifier' in joined:
        return 'apple'
    if 'isbn' in joined and 'channel' in joined:
        return 'd2d'
    if 'isbn' in joined and ('kobo' in joined or 'rakuten' in joined):
        return 'kobo'
    if 'transaction date' in joined and 'earnings' in joined:
        return 'google'
    if 'transaction type' in joined and ('acx' in joined or 'audible' in joined):
        return 'acx'

    return 'unknown'


def parse_file(filepath: str, platform: str, book_id: int = None) -> List[dict]:
    """Parse a royalty CSV file for the given platform.

    Args:
        filepath: Path to the CSV file
        platform: Platform name (kdp, apple, kobo, google, d2d, acx)
        book_id: Optional book_id to associate records with

    Returns:
        List of dicts matching the sales table schema
    """
    platform = platform.lower().strip()
    if platform not in PLATFORM_PARSERS:
        raise ParseError(f"Unknown platform: {platform}. Supported: {SUPPORTED_PLATFORMS}")

    import importlib
    module = importlib.import_module(PLATFORM_PARSERS[platform])
    return module.parse(filepath, book_id)
