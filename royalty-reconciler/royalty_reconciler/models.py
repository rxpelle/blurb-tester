from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class SaleRecord:
    """A single sale/royalty record from any platform."""
    book_id: Optional[int] = None
    date: str = ''
    units: int = 0
    royalty_amount: float = 0.0
    currency: str = 'USD'
    format: str = ''
    marketplace: str = 'US'
    platform: str = ''
    refund_amount: float = 0.0
    tax_withheld: float = 0.0
    royalty_rate: Optional[float] = None
    royalty_amount_usd: float = 0.0
    row_hash: str = ''


@dataclass
class Expense:
    """A business expense."""
    id: Optional[int] = None
    book_id: Optional[int] = None
    date: str = ''
    amount: float = 0.0
    currency: str = 'USD'
    category: str = ''
    description: str = ''
    tax_deductible: bool = True


@dataclass
class PnLReport:
    """Profit and loss report for a period."""
    period: str = ''
    gross_royalties: float = 0.0
    refunds: float = 0.0
    net_royalties: float = 0.0
    total_expenses: float = 0.0
    net_profit: float = 0.0
    by_platform: dict = field(default_factory=dict)
    by_book: dict = field(default_factory=dict)
    expense_breakdown: dict = field(default_factory=dict)


@dataclass
class TaxReport:
    """Schedule C tax report."""
    year: int = 0
    gross_receipts: float = 0.0
    returns_allowances: float = 0.0
    advertising: float = 0.0
    contract_labor: float = 0.0
    office_expenses: float = 0.0
    other_expenses: float = 0.0
    total_expenses: float = 0.0
    net_profit: float = 0.0
    platform_breakdown: dict = field(default_factory=dict)
    other_expense_details: List[dict] = field(default_factory=list)


@dataclass
class ReconciliationResult:
    """Result of comparing expected vs received payments."""
    platform: str = ''
    month: str = ''
    expected_royalties: float = 0.0
    received_payment: float = 0.0
    discrepancy: float = 0.0
    status: str = 'unknown'  # matched, underpaid, overpaid, missing
    records: int = 0
