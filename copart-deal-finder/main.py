#!/usr/bin/env python3
"""
Copart Deal Finder - Main Application

Automated system to identify great deals on damaged vehicles from
Oregon Copart auctions for repair and resale purposes.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger
from src.database import Database
from src.scraper import CopartScraper
from src.analysis import DealScorer
from src.reporting import ReportGenerator


def main():
    """Main application entry point."""
    logger = setup_logger('main')
    logger.info("="*60)
    logger.info("Copart Deal Finder - Oregon Edition")
    logger.info("="*60)

    try:
        # Initialize components
        logger.info("Initializing components...")
        config = Config()
        db = Database()
        scraper = CopartScraper(config)
        scorer = DealScorer(config)
        reporter = ReportGenerator(config)

        # Step 1: Scrape Oregon vehicles
        logger.info("\n[1/5] Scraping Oregon Copart listings...")
        logger.warning("NOTE: Web scraper is currently a placeholder.")
        logger.warning("Actual Copart scraping requires inspecting their website HTML structure.")
        logger.warning("For now, using empty dataset for demonstration.")

        vehicles = scraper.scrape_oregon_vehicles()

        if not vehicles:
            logger.warning("No vehicles scraped. This is expected with the placeholder scraper.")
            logger.info("To use this app with real data:")
            logger.info("1. Inspect Copart's website HTML structure")
            logger.info("2. Update scraper selectors in src/scraper/copart_scraper.py")
            logger.info("3. Or manually create test data for development")

            # Create sample data for testing
            vehicles = create_sample_data()
            logger.info(f"Created {len(vehicles)} sample vehicles for testing")

        # Step 2: Score vehicles
        logger.info(f"\n[2/5] Scoring {len(vehicles)} vehicles...")
        good_deals = scorer.score_and_filter_vehicles(vehicles)
        logger.info(f"Found {len(good_deals)} good deals")

        # Step 3: Save to database
        logger.info("\n[3/5] Saving vehicles to database...")
        for vehicle in good_deals:
            db.insert_vehicle(vehicle)
        logger.info(f"Saved {len(good_deals)} vehicles to database")

        # Step 4: Generate reports
        logger.info("\n[4/5] Generating reports...")

        # Daily report
        daily_report = reporter.generate_daily_report(good_deals)
        logger.info(f"Daily report: {daily_report}")

        # Text summary
        summary = reporter.generate_text_summary(good_deals)
        print(summary)

        # Check for upcoming auctions
        upcoming = db.get_upcoming_auctions(hours=12)
        if upcoming:
            logger.info(f"Found {len(upcoming)} vehicles auctioning in next 12 hours")
            pre_auction_report = reporter.generate_pre_auction_report(upcoming)
            logger.info(f"Pre-auction report: {pre_auction_report}")

        # Step 5: Summary
        logger.info("\n[5/5] Summary")
        logger.info(f"Total vehicles scraped: {len(vehicles)}")
        logger.info(f"Good deals found: {len(good_deals)}")
        logger.info(f"Top deal score: {good_deals[0]['deal_score']:.1f}" if good_deals else "N/A")

        logger.info("\n✅ Application completed successfully!")

        # Show next steps
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("\n1. Install Playwright: playwright install chromium")
        print("2. Update scraper with actual Copart HTML selectors")
        print("3. Configure settings in config/settings.yaml")
        print("4. Set up scheduling for automated runs")
        print("5. Configure email alerts (future enhancement)")
        print(f"\nDatabase: {db.db_path}")
        print(f"Reports: reports/daily/ and reports/pre_auction/")
        print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


def create_sample_data():
    """Create sample vehicle data for testing."""
    from random import randint, choice

    makes = ["Toyota", "Honda", "Ford", "Chevrolet", "BMW"]
    models = {
        "Toyota": ["Camry", "Corolla", "RAV4"],
        "Honda": ["Civic", "Accord", "CR-V"],
        "Ford": ["F-150", "Explorer", "Mustang"],
        "Chevrolet": ["Silverado", "Equinox", "Malibu"],
        "BMW": ["3 Series", "X5", "5 Series"]
    }
    damages = ["Front End", "Rear End", "Hail", "Minor Dent/Scratches", "Side"]
    locations = ["OR - PORTLAND NORTH", "OR - PORTLAND SOUTH", "OR - EUGENE"]

    vehicles = []

    for i in range(15):
        make = choice(makes)
        model = choice(models[make])
        year = randint(2015, 2023)
        retail_value = randint(15000, 45000)
        current_bid = randint(int(retail_value * 0.3), int(retail_value * 0.7))

        vehicle = {
            'lot_number': 100000 + i,
            'vin': f"1HGBH{randint(10,99)}8H7A{randint(100000,999999)}",
            'year': year,
            'make': make,
            'model': model,
            'trim': "Base",
            'body_style': "Sedan" if "Series" in model else "SUV",
            'odometer': randint(20000, 120000),
            'odometer_status': 'ACTUAL',
            'engine_type': '2.4L I4',
            'transmission': 'Automatic',
            'drivetrain': 'FWD',
            'fuel_type': 'Gasoline',
            'title_type': choice(['Salvage', 'Clean', 'Rebuilt']),
            'title_state': 'OR',
            'primary_damage': choice(damages),
            'secondary_damage': None,
            'has_keys': choice([True, False]),
            'runs_drives': choice([True, True, False]),  # 2/3 chance of yes
            'engine_starts': True,
            'transmission_engages': True,
            'location': choice(locations),
            'sale_date': datetime.now().isoformat(),
            'sale_type': 'Wholesale',
            'seller': 'Insurance Co',
            'current_bid': float(current_bid),
            'buy_now_price': None,
            'estimated_retail_value': float(retail_value),
            'reserve_met': choice([True, False]),
            'autograde_score': round(randint(25, 50) / 10, 1),
            'autocheck_score': randint(60, 95),
            'image_urls': [],
            'detail_page_url': f'https://www.copart.com/lot/{100000 + i}',
            'notes': 'Sample data for testing',
        }

        vehicles.append(vehicle)

    return vehicles


if __name__ == "__main__":
    main()
