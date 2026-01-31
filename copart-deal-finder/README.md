# Copart Deal Finder - Oregon Edition

Automated system to identify great deals on damaged vehicles from Oregon Copart auctions for repair and resale purposes.

## Features

- 🔍 **Automated Web Scraping** - Scrapes Copart listings for Oregon locations (Portland North, Portland South, Eugene)
- 📊 **Smart Deal Scoring** - Analyzes vehicles based on value gap, repair costs, and risk factors
- 📧 **Pre-Auction Alerts** - Sends reports 12 hours before auctions
- 📈 **Daily Reports** - Top 20 Oregon deals delivered daily
- 💾 **SQLite Database** - Tracks vehicles, bids, and pricing history
- 🎯 **Profit Estimation** - Calculates estimated profit after repairs and fees

## Deal Scoring Algorithm

The app scores each vehicle based on:

**Base Score:**
- Value Gap (Retail Value - Current Bid) × 100

**Bonuses:**
- Runs & Drives: +10 points
- Has Keys: +5 points
- Low Mileage (<50k): +5 points
- Clean Title: +15 points

**Penalties:**
- Flood Damage: -20 points
- Frame Damage: -25 points
- No Keys + Mechanical: -15 points
- Unknown Odometer: -10 points

**Target Scores:**
- 80+: Excellent deal
- 60-79: Good deal
- 50-59: Fair deal
- <50: Skip

## Installation

### Prerequisites
- Python 3.11+
- Playwright (for web scraping)

### Setup

```bash
# 1. Navigate to project directory
cd copart-deal-finder

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Configure settings
# Edit config/settings.yaml with your preferences
```

## Configuration

### settings.yaml

```yaml
search:
  makes: ["Honda", "Toyota", "Ford", "BMW"]  # Target makes
  max_year: 2024
  min_year: 2010
  max_mileage: 150000

location:
  state: "OR"  # Oregon only
  auction_locations:
    - "OR - PORTLAND NORTH"
    - "OR - PORTLAND SOUTH"
    - "OR - EUGENE"

scoring:
  min_value_gap_percent: 30      # Minimum value gap
  max_repair_cost_percent: 40    # Maximum repair cost
  min_autograde_score: 3.0       # Minimum quality score

alerts:
  pre_auction_report_hours: 12   # Hours before auction
  min_deal_score: 60             # Minimum score to report
```

## Usage

### Run the Application

```bash
python main.py
```

This will:
1. Scrape Oregon Copart listings
2. Score and filter vehicles
3. Save to database
4. Generate HTML reports

### Output

- **Database**: `data/copart.db`
- **Daily Reports**: `reports/daily/daily_report_YYYYMMDD.html`
- **Pre-Auction Reports**: `reports/pre_auction/pre_auction_YYYYMMDD_HHMM.html`
- **Logs**: `logs/`

## Project Structure

```
copart-deal-finder/
├── src/
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── copart_scraper.py      # Web scraping logic
│   ├── database/
│   │   ├── __init__.py
│   │   └── models.py               # Database schema
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── scoring.py              # Deal scoring algorithm
│   ├── reporting/
│   │   ├── __init__.py
│   │   └── report_generator.py    # HTML/text reports
│   └── utils/
│       ├── __init__.py
│       ├── config.py               # Configuration manager
│       └── logging.py              # Logging setup
├── config/
│   ├── settings.yaml               # User preferences
│   └── damage_costs.yaml           # Repair cost matrix
├── data/
│   └── copart.db                   # SQLite database
├── reports/
│   ├── daily/                      # Daily reports
│   └── pre_auction/                # Pre-auction alerts
├── logs/                           # Application logs
├── main.py                         # Entry point
├── requirements.txt
└── README.md
```

## Current Status

### ✅ Completed
- Project structure
- Database schema and models
- Configuration system
- Deal scoring algorithm
- Report generation (HTML & text)
- Sample data generation

### 🚧 In Progress
- Web scraper implementation (placeholder selectors)

### 📋 To Do
- Update scraper with actual Copart HTML selectors
- Implement scheduling for automated runs
- Add email notifications
- Create pre-auction scheduler
- Add machine learning for price prediction

## Important Notes

### Web Scraping
The web scraper currently uses **placeholder selectors**. To use with real Copart data:

1. Inspect Copart's website HTML structure
2. Update selectors in `src/scraper/copart_scraper.py`
3. Test with small batches first
4. Respect Copart's terms of service and robots.txt

### Legal Considerations
- This tool is for **personal use only**
- Respect Copart's terms of service
- Use reasonable rate limiting (2+ seconds between requests)
- Consider registering for a Copart account for better data access

## Example Output

```
============================================================
  COPART DEAL SUMMARY - 2025-12-26 14:30
============================================================

Total Deals: 12

1. 2021 Toyota RAV4
   Score: 85.5 | Lot: 100001 | Bid: $12,500
   Location: OR - PORTLAND NORTH | Damage: Front End
   Est. Profit: $8,250

2. 2020 Honda Civic
   Score: 78.2 | Lot: 100003 | Bid: $9,800
   Location: OR - EUGENE | Damage: Hail
   Est. Profit: $6,500
```

## Scheduled Automation

To run automatically, set up a cron job:

```bash
# Run every 6 hours
0 */6 * * * cd /path/to/copart-deal-finder && python main.py
```

## Support

For issues or questions, check the logs in `logs/` directory.

## License

This project is for personal use. Not affiliated with Copart.

---

**Built with ❤️ for Oregon car flippers**
