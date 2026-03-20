"""Configuration management for series-bible-generator."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Default bible document types and their expected filename patterns
BIBLE_DOCUMENT_TYPES = {
    "timeline": "master_timeline",
    "bloodline": "bloodline_tracker",
    "keys": "seven_keys_tracker",
    "terminology": "terminology_glossary",
    "network": "network_evolution",
    "continuity": "continuity_gaps",
    "collapse": "collapse_and_rise",
    "dynamics": "system_dynamics",
}

# Default data directory
DEFAULT_DATA_DIR = Path.home() / ".series-bible-generator"


@dataclass
class Config:
    """Application configuration."""
    anthropic_api_key: Optional[str] = None
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    data_dir: Path = DEFAULT_DATA_DIR
    bible_prefix: str = "SERIES_BIBLE_"

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            model=os.environ.get("SERIES_BIBLE_MODEL", "claude-sonnet-4-20250514"),
            data_dir=Path(os.environ.get("SERIES_BIBLE_DATA_DIR", str(DEFAULT_DATA_DIR))),
        )

    @property
    def has_api_key(self) -> bool:
        """Check if API key is configured."""
        return bool(self.anthropic_api_key)

    @property
    def db_path(self) -> Path:
        """Path to SQLite database."""
        return self.data_dir / "series_bible.db"
