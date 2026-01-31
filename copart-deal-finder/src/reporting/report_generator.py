import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils import Config, setup_logger


class ReportGenerator:
    """Generate deal reports in various formats."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger('report_generator')
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def generate_daily_report(self, vehicles: List[Dict[str, Any]]) -> str:
        """
        Generate daily deal summary report.

        Args:
            vehicles: List of vehicles (should be pre-scored and filtered)

        Returns:
            Path to generated report file
        """
        self.logger.info(f"Generating daily report for {len(vehicles)} vehicles")

        # Sort vehicles by score
        sorted_vehicles = sorted(vehicles, key=lambda x: x.get('deal_score', 0), reverse=True)

        # Take top 20
        top_deals = sorted_vehicles[:20]

        # Generate HTML report
        html = self._generate_html_report(top_deals, "Daily Top Deals - Oregon Copart Auctions")

        # Save to file
        filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = self.reports_dir / "daily" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            f.write(html)

        self.logger.info(f"Daily report saved to {filepath}")
        return str(filepath)

    def generate_pre_auction_report(self, vehicles: List[Dict[str, Any]], hours_ahead: int = 12) -> str:
        """
        Generate pre-auction alert report for vehicles auctioning soon.

        Args:
            vehicles: List of vehicles auctioning in the next X hours
            hours_ahead: Number of hours ahead to report

        Returns:
            Path to generated report file
        """
        self.logger.info(f"Generating pre-auction report for {len(vehicles)} vehicles")

        # Sort by auction time
        sorted_vehicles = sorted(vehicles, key=lambda x: x.get('sale_date', ''))

        # Generate HTML report
        title = f"⏰ Pre-Auction Alert - {hours_ahead} Hour Notice"
        html = self._generate_html_report(sorted_vehicles, title, pre_auction=True)

        # Save to file
        filename = f"pre_auction_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        filepath = self.reports_dir / "pre_auction" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            f.write(html)

        self.logger.info(f"Pre-auction report saved to {filepath}")
        return str(filepath)

    def _generate_html_report(self, vehicles: List[Dict[str, Any]], title: str,
                             pre_auction: bool = False) -> str:
        """Generate HTML report content."""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .vehicle-card {{
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .vehicle-title {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .score-badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            color: white;
            font-weight: bold;
            margin-right: 10px;
        }}
        .score-excellent {{ background-color: #27ae60; }}
        .score-good {{ background-color: #3498db; }}
        .score-fair {{ background-color: #f39c12; }}
        .info-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin: 10px 0;
        }}
        .info-item {{
            padding: 5px;
        }}
        .label {{
            font-weight: bold;
            color: #7f8c8d;
        }}
        .value {{
            color: #2c3e50;
        }}
        .damage {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .profit {{
            color: #27ae60;
            font-weight: bold;
            font-size: 16px;
        }}
        .auction-time {{
            color: #e74c3c;
            font-weight: bold;
            font-size: 14px;
        }}
        .link {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 15px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 3px;
        }}
        .link:hover {{
            background-color: #2980b9;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Vehicles: {len(vehicles)}</p>
    </div>
"""

        # Add vehicle cards
        for idx, vehicle in enumerate(vehicles, 1):
            score = vehicle.get('deal_score', 0)
            score_class = 'score-excellent' if score >= 80 else ('score-good' if score >= 60 else 'score-fair')

            profit = vehicle.get('estimated_profit', 0)
            profit_str = f"${profit:,.0f}" if profit and profit > 0 else "N/A"

            sale_date = vehicle.get('sale_date', 'Unknown')
            auction_warning = ""
            if pre_auction and sale_date != 'Unknown':
                auction_warning = f'<div class="auction-time">⏰ Auction: {sale_date}</div>'

            html += f"""
    <div class="vehicle-card">
        <div class="vehicle-title">
            #{idx} - {vehicle.get('year', 'N/A')} {vehicle.get('make', 'N/A')} {vehicle.get('model', 'N/A')}
            <span class="score-badge {score_class}">Score: {score:.1f}</span>
        </div>

        {auction_warning}

        <div class="info-row">
            <div class="info-item">
                <span class="label">Lot #:</span>
                <span class="value">{vehicle.get('lot_number', 'N/A')}</span>
            </div>
            <div class="info-item">
                <span class="label">Location:</span>
                <span class="value">{vehicle.get('location', 'N/A')}</span>
            </div>
            <div class="info-item">
                <span class="label">Odometer:</span>
                <span class="value">{vehicle.get('odometer', 'N/A'):,} mi</span>
            </div>
        </div>

        <div class="info-row">
            <div class="info-item">
                <span class="label">Current Bid:</span>
                <span class="value">${vehicle.get('current_bid', 0):,.0f}</span>
            </div>
            <div class="info-item">
                <span class="label">Retail Value:</span>
                <span class="value">${vehicle.get('estimated_retail_value', 0):,.0f}</span>
            </div>
            <div class="info-item">
                <span class="label">Est. Profit:</span>
                <span class="profit">{profit_str}</span>
            </div>
        </div>

        <div class="info-row">
            <div class="info-item">
                <span class="label">Damage:</span>
                <span class="damage">{vehicle.get('primary_damage', 'Unknown')}</span>
            </div>
            <div class="info-item">
                <span class="label">Run/Drive:</span>
                <span class="value">{'Yes' if vehicle.get('runs_drives') else 'No'}</span>
            </div>
            <div class="info-item">
                <span class="label">Keys:</span>
                <span class="value">{'Yes' if vehicle.get('has_keys') else 'No'}</span>
            </div>
        </div>

        {f'<a href="{vehicle.get("detail_page_url")}" class="link" target="_blank">View on Copart</a>' if vehicle.get('detail_page_url') else ''}
    </div>
"""

        html += """
</body>
</html>
"""

        return html

    def generate_text_summary(self, vehicles: List[Dict[str, Any]]) -> str:
        """
        Generate a simple text summary of deals.

        Args:
            vehicles: List of vehicles

        Returns:
            Text summary string
        """
        if not vehicles:
            return "No deals found."

        summary = f"\n{'='*60}\n"
        summary += f"  COPART DEAL SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        summary += f"{'='*60}\n\n"
        summary += f"Total Deals: {len(vehicles)}\n\n"

        for idx, vehicle in enumerate(vehicles[:10], 1):
            summary += f"{idx}. {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}\n"
            summary += f"   Score: {vehicle.get('deal_score', 0):.1f} | "
            summary += f"Lot: {vehicle.get('lot_number')} | "
            summary += f"Bid: ${vehicle.get('current_bid', 0):,.0f}\n"
            summary += f"   Location: {vehicle.get('location')} | "
            summary += f"Damage: {vehicle.get('primary_damage')}\n"
            summary += f"   Est. Profit: ${vehicle.get('estimated_profit', 0):,.0f}\n\n"

        return summary
