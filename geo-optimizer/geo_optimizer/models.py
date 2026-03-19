from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GEOScore:
    overall_score: float = 0.0
    category_scores: dict[str, float] = field(default_factory=dict)
    grade: str = 'F'
    top_issues: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    category: str = ''
    score: float = 0.0
    max_score: float = 0.0
    checks: list[dict] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        if self.max_score == 0:
            return 0.0
        return round(self.score / self.max_score * 100, 1)


@dataclass
class Recommendation:
    priority: str = 'medium'  # high, medium, low
    category: str = ''
    issue: str = ''
    fix: str = ''
    impact: float = 0.0  # estimated score improvement
