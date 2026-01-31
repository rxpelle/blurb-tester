import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for Copart Deal Finder."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.settings = self._load_yaml("settings.yaml")
        self.damage_costs = self._load_yaml("damage_costs.yaml")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file."""
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split('.')
        value = self.settings

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_damage_cost(self, damage_type: str) -> Dict[str, int]:
        """Get repair cost estimate for a damage type."""
        costs = self.damage_costs.get('damage_costs', {})
        return costs.get(damage_type, costs.get('Unknown', {'min': 25, 'max': 35}))

    def get_bonus(self, bonus_type: str) -> int:
        """Get bonus points for a feature."""
        return self.damage_costs.get('bonuses', {}).get(bonus_type, 0)

    def get_penalty(self, penalty_type: str) -> int:
        """Get penalty points for a risk factor."""
        return self.damage_costs.get('penalties', {}).get(penalty_type, 0)

    @property
    def search_makes(self):
        return self.get('search.makes', [])

    @property
    def oregon_locations(self):
        return self.get('location.auction_locations', [])

    @property
    def min_deal_score(self):
        return self.get('alerts.min_deal_score', 60)

    @property
    def rate_limit_seconds(self):
        return self.get('scraping.rate_limit_seconds', 2)

    @property
    def user_agent(self):
        return self.get('scraping.user_agent', 'Mozilla/5.0')
