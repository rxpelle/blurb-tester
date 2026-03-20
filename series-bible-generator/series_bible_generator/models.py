"""Data models for series bible entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Character:
    """A character extracted from the series bible or manuscript."""
    name: str
    aliases: list = field(default_factory=list)
    description: str = ""
    first_appearance_book: str = ""
    first_appearance_chapter: str = ""
    era: str = ""
    generation_absolute: Optional[int] = None
    generation_local: Optional[int] = None
    status: str = ""  # "alive", "dead", "unknown"
    role: str = ""  # "protagonist", "antagonist", "supporting", "mentioned"
    network: str = ""  # "defensive", "offensive", "neutral", "unknown"
    relationships: list = field(default_factory=list)
    traits: list = field(default_factory=list)
    locations: list = field(default_factory=list)
    source_file: str = ""

    def __post_init__(self):
        if self.status and self.status not in ("alive", "dead", "unknown"):
            raise ValueError(f"Invalid status: {self.status}")
        if self.role and self.role not in ("protagonist", "antagonist", "supporting", "mentioned"):
            raise ValueError(f"Invalid role: {self.role}")

    @property
    def all_names(self) -> list:
        """All names including aliases."""
        return [self.name] + self.aliases


@dataclass
class TimelineEvent:
    """A timeline event from the series bible."""
    date: str
    year_numeric: Optional[int] = None  # negative for BCE
    description: str = ""
    book: str = ""
    chapter: str = ""
    era: str = ""
    characters_involved: list = field(default_factory=list)
    location: str = ""
    significance: str = ""  # "major", "minor", "background"
    source_file: str = ""

    def __post_init__(self):
        if self.significance and self.significance not in ("major", "minor", "background"):
            raise ValueError(f"Invalid significance: {self.significance}")


@dataclass
class GlossaryTerm:
    """A term from the terminology glossary."""
    term: str
    definition: str = ""
    correct_usage: str = ""
    incorrect_forms: list = field(default_factory=list)
    era_restrictions: list = field(default_factory=list)
    book_specific_notes: dict = field(default_factory=dict)
    source_file: str = ""


@dataclass
class Artifact:
    """A significant object tracked across the series (e.g., bronze keys)."""
    name: str
    description: str = ""
    artifact_type: str = ""  # "key", "document", "weapon", etc.
    created_date: str = ""
    created_by: str = ""
    current_holder: str = ""
    movement_log: list = field(default_factory=list)  # list of (date, holder, location)
    properties: dict = field(default_factory=dict)
    source_file: str = ""


@dataclass
class Location:
    """A significant location in the series."""
    name: str
    aliases: list = field(default_factory=list)
    description: str = ""
    era: str = ""
    books_featured: list = field(default_factory=list)
    characters_present: list = field(default_factory=list)
    source_file: str = ""


@dataclass
class BibleDocument:
    """A parsed series bible document."""
    doc_type: str  # matches BIBLE_DOCUMENT_TYPES keys
    title: str
    file_path: str
    content: str
    sections: list = field(default_factory=list)  # list of (heading, content)
    characters: list = field(default_factory=list)
    events: list = field(default_factory=list)
    terms: list = field(default_factory=list)
    artifacts: list = field(default_factory=list)
    locations: list = field(default_factory=list)
    parsed_date: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExtractionResult:
    """Results from extracting entities from a manuscript."""
    manuscript_path: str
    extraction_date: str = field(default_factory=lambda: datetime.now().isoformat())
    chapters_processed: int = 0
    characters: list = field(default_factory=list)
    events: list = field(default_factory=list)
    terms: list = field(default_factory=list)
    locations: list = field(default_factory=list)
    artifacts: list = field(default_factory=list)

    @property
    def total_entities(self) -> int:
        return (len(self.characters) + len(self.events) + len(self.terms)
                + len(self.locations) + len(self.artifacts))


@dataclass
class ValidationIssue:
    """A single issue found during bible validation."""
    severity: str  # "error", "warning", "info"
    category: str  # "character", "timeline", "terminology", "artifact", "continuity"
    description: str
    location: str
    bible_reference: str = ""
    suggestion: str = ""

    VALID_SEVERITIES = ("error", "warning", "info")
    VALID_CATEGORIES = ("character", "timeline", "terminology", "artifact", "continuity")

    def __post_init__(self):
        if self.severity not in self.VALID_SEVERITIES:
            raise ValueError(f"Invalid severity: {self.severity}")
        if self.category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {self.category}")


@dataclass
class ComplianceReport:
    """A compliance report for a manuscript against the series bible."""
    manuscript_path: str
    bible_path: str
    report_date: str = field(default_factory=lambda: datetime.now().isoformat())
    score: float = 0.0
    total_checks: int = 0
    passed_checks: int = 0
    issues: list = field(default_factory=list)  # list[ValidationIssue]
    chapters_validated: list = field(default_factory=list)
    summary: str = ""

    def add_issue(self, issue: ValidationIssue):
        """Add an issue and update counts."""
        self.issues.append(issue)
        self.total_checks += 1

    def add_pass(self):
        """Record a passed check."""
        self.total_checks += 1
        self.passed_checks += 1

    def calculate_score(self):
        """Calculate compliance score."""
        if self.total_checks == 0:
            self.score = 100.0
            return
        self.score = round((self.passed_checks / self.total_checks) * 100, 1)

    @property
    def errors(self) -> list:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def info_items(self) -> list:
        return [i for i in self.issues if i.severity == "info"]


@dataclass
class QueryResult:
    """Result from a bible query."""
    query: str
    result_type: str  # "character", "event", "term", "artifact", "location", "general"
    results: list = field(default_factory=list)
    context: str = ""
    sources: list = field(default_factory=list)
