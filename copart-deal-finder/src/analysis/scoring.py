import sys
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils import Config, setup_logger


class DealScorer:
    """Calculate deal scores for vehicles based on multiple factors."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger('deal_scorer')

    def calculate_deal_score(self, vehicle: Dict[str, Any]) -> float:
        """
        Calculate overall deal score for a vehicle.

        Deal Score Formula:
        - Base: Value Gap × 100
        - Subtract: Estimated Repair % × 50
        - Add: Bonuses (Run/Drive, Keys, Low Mileage, Clean Title)
        - Subtract: Penalties (Risk factors)

        Args:
            vehicle: Vehicle data dictionary

        Returns:
            Deal score (0-100+, higher is better)
        """
        score = 0.0

        # Calculate value gap
        value_gap_pct = self._calculate_value_gap(vehicle)
        if value_gap_pct is None:
            self.logger.warning(f"Cannot calculate value gap for lot {vehicle.get('lot_number')}")
            return 0.0

        # Base score from value gap
        score += value_gap_pct * 100

        # Subtract repair cost impact
        repair_cost_pct = self._estimate_repair_cost_percentage(vehicle)
        vehicle['estimated_repair_cost_pct'] = repair_cost_pct
        score -= repair_cost_pct * 50

        # Add bonuses
        score += self._calculate_bonuses(vehicle)

        # Subtract penalties
        score -= self._calculate_penalties(vehicle)

        # Ensure score is not negative
        score = max(0.0, score)

        self.logger.debug(f"Lot {vehicle.get('lot_number')}: Score={score:.2f}, "
                         f"ValueGap={value_gap_pct:.1%}, RepairCost={repair_cost_pct:.1%}")

        return round(score, 2)

    def _calculate_value_gap(self, vehicle: Dict[str, Any]) -> Optional[float]:
        """
        Calculate value gap percentage.

        Value Gap = (Estimated Retail - Current Bid) / Estimated Retail

        Returns:
            Value gap as decimal (e.g., 0.40 for 40%)
        """
        retail = vehicle.get('estimated_retail_value', 0)
        bid = vehicle.get('current_bid', 0)

        if retail <= 0:
            return None

        value_gap = (retail - bid) / retail
        return max(0.0, value_gap)

    def _estimate_repair_cost_percentage(self, vehicle: Dict[str, Any]) -> float:
        """
        Estimate repair cost as percentage of retail value.

        Returns:
            Repair cost percentage as decimal (e.g., 0.25 for 25%)
        """
        damage_type = vehicle.get('primary_damage', 'Unknown')
        damage_costs = self.config.get_damage_cost(damage_type)

        # Use average of min and max
        avg_cost_pct = (damage_costs['min'] + damage_costs['max']) / 2

        # Adjust based on run/drive status
        if not vehicle.get('runs_drives', False):
            # Add 5-10% if doesn't run/drive
            avg_cost_pct += 7.5

        # Adjust based on mileage
        odometer = vehicle.get('odometer', 0)
        if odometer > 150000:
            avg_cost_pct += 5  # High mileage adds risk

        return avg_cost_pct / 100  # Convert to decimal

    def _calculate_bonuses(self, vehicle: Dict[str, Any]) -> float:
        """Calculate bonus points for positive features."""
        bonus_points = 0.0

        # Run and drive bonus
        if vehicle.get('runs_drives', False):
            bonus_points += self.config.get_bonus('runs_drives')

        # Has keys bonus
        if vehicle.get('has_keys', False):
            bonus_points += self.config.get_bonus('has_keys')

        # Low mileage bonus (< 50k miles)
        odometer = vehicle.get('odometer', 0)
        if 0 < odometer < 50000:
            bonus_points += self.config.get_bonus('low_mileage')

        # Clean title bonus
        title_type = vehicle.get('title_type', '').lower()
        if 'clean' in title_type:
            bonus_points += self.config.get_bonus('clean_title')

        return bonus_points

    def _calculate_penalties(self, vehicle: Dict[str, Any]) -> float:
        """Calculate penalty points for risk factors."""
        penalty_points = 0.0

        # No keys + mechanical damage
        if not vehicle.get('has_keys', True) and 'mechanical' in vehicle.get('primary_damage', '').lower():
            penalty_points += self.config.get_penalty('no_keys_and_mechanical')

        # Flood damage
        if 'flood' in vehicle.get('primary_damage', '').lower():
            penalty_points += self.config.get_penalty('flood_damage')

        # Frame damage
        if 'frame' in vehicle.get('primary_damage', '').lower():
            penalty_points += self.config.get_penalty('frame_damage')

        # Odometer unknown
        odometer_status = vehicle.get('odometer_status', '').upper()
        if odometer_status in ['TMU', 'EXEMPT', 'UNKNOWN']:
            penalty_points += self.config.get_penalty('odometer_unknown')

        return penalty_points

    def calculate_estimated_profit(self, vehicle: Dict[str, Any]) -> Optional[float]:
        """
        Calculate estimated profit potential.

        Profit = Retail Value - Current Bid - Estimated Repair Cost - Fees

        Args:
            vehicle: Vehicle data with deal_score already calculated

        Returns:
            Estimated profit in dollars
        """
        retail = vehicle.get('estimated_retail_value', 0)
        bid = vehicle.get('current_bid', 0)
        repair_cost_pct = vehicle.get('estimated_repair_cost_pct', 0.25)

        if retail <= 0:
            return None

        repair_cost = retail * repair_cost_pct
        fees = bid * 0.10  # Estimate 10% in auction fees

        profit = retail - bid - repair_cost - fees

        return round(profit, 2)

    def is_good_deal(self, vehicle: Dict[str, Any]) -> bool:
        """
        Determine if a vehicle is a good deal based on scoring thresholds.

        Args:
            vehicle: Vehicle data with deal_score calculated

        Returns:
            True if vehicle meets minimum criteria
        """
        score = vehicle.get('deal_score', 0)
        min_score = self.config.min_deal_score

        if score < min_score:
            return False

        # Additional filters
        value_gap_pct = self._calculate_value_gap(vehicle)
        if value_gap_pct is None or value_gap_pct < self.config.get('scoring.min_value_gap_percent', 30) / 100:
            return False

        repair_cost_pct = vehicle.get('estimated_repair_cost_pct', 0)
        if repair_cost_pct > self.config.get('scoring.max_repair_cost_percent', 40) / 100:
            return False

        return True

    def score_and_filter_vehicles(self, vehicles: list) -> list:
        """
        Score all vehicles and filter to good deals only.

        Args:
            vehicles: List of vehicle dictionaries

        Returns:
            List of vehicles with scores, filtered to good deals
        """
        scored_vehicles = []

        for vehicle in vehicles:
            # Calculate deal score
            score = self.calculate_deal_score(vehicle)
            vehicle['deal_score'] = score

            # Calculate estimated profit
            profit = self.calculate_estimated_profit(vehicle)
            vehicle['estimated_profit'] = profit

            # Filter to good deals
            if self.is_good_deal(vehicle):
                scored_vehicles.append(vehicle)

        # Sort by score descending
        scored_vehicles.sort(key=lambda x: x.get('deal_score', 0), reverse=True)

        self.logger.info(f"Scored {len(vehicles)} vehicles, {len(scored_vehicles)} are good deals")

        return scored_vehicles
