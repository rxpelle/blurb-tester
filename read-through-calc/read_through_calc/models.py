from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class BookInfo:
    """Lightweight book info pulled from shared DB."""
    id: int
    asin: str = ''
    title: str = ''
    series_name: str = ''
    series_position: Optional[int] = None
    kenp_baseline: Optional[int] = None


@dataclass
class ReadThroughResult:
    """Read-through rate between two consecutive books."""
    from_book: str
    to_book: str
    from_position: int
    to_position: int
    from_units: int
    to_units: int
    overall_rate: float
    cohort_rate: Optional[float] = None
    cohort_periods: int = 0


@dataclass
class ReadThroughReport:
    """Full read-through report for a series."""
    series_name: str
    books: List[BookInfo] = field(default_factory=list)
    rates: List[ReadThroughResult] = field(default_factory=list)
    cumulative_rate: float = 0.0


@dataclass
class LTVReport:
    """Lifetime reader value for a series."""
    series_name: str
    books: List[BookInfo] = field(default_factory=list)
    read_through_rates: List[float] = field(default_factory=list)
    cumulative_rates: List[float] = field(default_factory=list)
    per_book_royalty: List[float] = field(default_factory=list)
    per_book_kenp_value: List[float] = field(default_factory=list)
    per_book_ltv_contribution: List[float] = field(default_factory=list)
    total_ltv: float = 0.0
    kenp_rate: float = 0.0045


@dataclass
class PricingScenario:
    """What-if pricing scenario results."""
    series_name: str
    books: List[BookInfo] = field(default_factory=list)
    prices: List[float] = field(default_factory=list)
    royalty_rates: List[float] = field(default_factory=list)
    per_book_royalty: List[float] = field(default_factory=list)
    read_through_rates: List[float] = field(default_factory=list)
    cumulative_rates: List[float] = field(default_factory=list)
    per_book_ltv_contribution: List[float] = field(default_factory=list)
    total_ltv: float = 0.0
    revenue_per_100: float = 0.0
    kenp_rate: float = 0.0045
