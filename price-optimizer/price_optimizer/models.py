from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class PricePoint:
    """Metrics for a book at a specific price."""
    price: float
    days_active: int = 0
    total_units: int = 0
    avg_daily_units: float = 0.0
    avg_bsr: Optional[float] = None
    daily_revenue: float = 0.0
    royalty_per_unit: float = 0.0
    start_date: str = ''
    end_date: str = ''


@dataclass
class ElasticityResult:
    """Price elasticity between two price points."""
    price_from: float
    price_to: float
    pct_price_change: float
    pct_quantity_change: float
    elasticity: float
    interpretation: str = ''


@dataclass
class Experiment:
    """A price experiment configuration."""
    asin: str
    prices: List[float] = field(default_factory=list)
    duration_days: int = 14
    started_at: str = ''
    current_price_index: int = 0
    status: str = 'running'  # running, completed, cancelled


@dataclass
class Recommendation:
    """Optimal price recommendation."""
    recommended_price: Optional[float] = None
    estimated_daily_revenue: float = 0.0
    estimated_daily_units: float = 0.0
    estimated_royalty: float = 0.0
    confidence: str = 'low'  # low, medium, high
    reasoning: str = ''
    price_points_analyzed: int = 0


@dataclass
class RoyaltyResult:
    """Result of a royalty calculation."""
    price: float
    format: str = 'ebook'
    marketplace: str = 'US'
    royalty_amount: float = 0.0
    royalty_rate: float = 0.0
    tier: str = ''
    delivery_cost: float = 0.0
    print_cost: float = 0.0
