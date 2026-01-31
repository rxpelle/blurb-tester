#!/usr/bin/env python3
"""
Run the complete Copart Deal Finder application.

This script:
1. Logs in with your credentials
2. Searches for Oregon vehicles
3. Extracts vehicle data
4. Scores deals
5. Saves to database
6. Generates reports
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger
from src.database import Database
from src.scraper import CopartScraper
from src.scraper.vehicle_extractor import VehicleExtractor
from src.analysis import DealScorer
from src.reporting import ReportGenerator


def main():
    """Run the full application."""
    logger = setup_logger('main')

    print("\n" + "="*60)
    print("COPART DEAL FINDER - FULL APPLICATION")
    print("="*60)

    # Load credentials
    load_dotenv('config/.env')
    username = os.getenv('COPART_USERNAME')
    password = os.getenv('COPART_PASSWORD')

    if not username or not password:
        print("\n❌ Error: Credentials not found in config/.env")
        return

    print(f"\n✅ Loaded credentials for: {username}")

    # Initialize components
    config = Config()
    db = Database()
    scorer = DealScorer(config)
    reporter = ReportGenerator(config)
    extractor = VehicleExtractor()

    print("\n" + "="*60)
    print("STEP 1: Login to Copart")
    print("="*60)

    scraper = CopartScraper(config, username=username, password=password, use_stealth=True)

    try:
        # Start browser
        scraper.start_browser()

        # Login
        if not scraper.login():
            print("❌ Login failed - see logs/after_login.png")
            return

        print("✅ Successfully logged in!")

        print("\n" + "="*60)
        print("STEP 2: Search for Vehicles")
        print("="*60)

        # Create search page
        page = scraper.context.new_page()

        # Search for Toyota vehicles (you can change this)
        search_query = "Toyota"
        print(f"\n🔍 Searching for: {search_query}")

        page.goto(f"https://www.copart.com/lotSearchResults/?free=true&query={search_query}", timeout=60000)

        import time
        print("   Waiting for results to load...")
        time.sleep(10)

        # Save for debugging
        page.screenshot(path="logs/search_page.png", full_page=True)
        print("   Screenshot saved: logs/search_page.png")

        print("\n" + "="*60)
        print("STEP 3: Extract Vehicle Data")
        print("="*60)

        vehicles = extractor.extract_from_page(page)
        print(f"\n✅ Extracted {len(vehicles)} vehicles")

        if vehicles:
            # Show sample
            print("\n📋 Sample vehicle:")
            sample = vehicles[0]
            for key, value in list(sample.items())[:10]:
                if value:
                    print(f"   {key}: {value}")

        page.close()

        if not vehicles:
            print("\n⚠️  No vehicles extracted")
            print("   This might mean:")
            print("   1. Search returned no results")
            print("   2. Page structure is different than expected")
            print("   3. Need to wait longer for page to load")
            print("\n   Check logs/search_page.png to see what loaded")

            # Try with sample data instead
            print("\n   Using sample data for demonstration...")
            from main import create_sample_data
            vehicles = create_sample_data()

        print("\n" + "="*60)
        print("STEP 4: Score Deals")
        print("="*60)

        good_deals = scorer.score_and_filter_vehicles(vehicles)
        print(f"\n✅ Found {len(good_deals)} good deals (score ≥ 60)")

        if good_deals:
            print("\n🏆 Top 3 Deals:")
            for i, vehicle in enumerate(good_deals[:3], 1):
                print(f"\n   #{i} - {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}")
                print(f"       Lot: {vehicle.get('lot_number')}")
                print(f"       Score: {vehicle.get('deal_score', 0):.1f}")
                print(f"       Est. Profit: ${vehicle.get('estimated_profit', 0):,.0f}")

        print("\n" + "="*60)
        print("STEP 5: Save to Database")
        print("="*60)

        saved_count = 0
        for vehicle in good_deals:
            if db.insert_vehicle(vehicle):
                saved_count += 1

        print(f"\n✅ Saved {saved_count} vehicles to database")

        print("\n" + "="*60)
        print("STEP 6: Generate Reports")
        print("="*60)

        # Daily report
        daily_report = reporter.generate_daily_report(good_deals)
        print(f"\n📄 Daily report: {daily_report}")

        # Text summary
        summary = reporter.generate_text_summary(good_deals)
        print(summary)

        # Check for upcoming auctions
        upcoming = db.get_upcoming_auctions(hours=12)
        if upcoming:
            pre_auction_report = reporter.generate_pre_auction_report(upcoming)
            print(f"⏰ Pre-auction report: {pre_auction_report}")

        print("\n" + "="*60)
        print("✅ APPLICATION COMPLETE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   - Vehicles found: {len(vehicles)}")
        print(f"   - Good deals: {len(good_deals)}")
        print(f"   - Saved to database: {saved_count}")
        print(f"   - Top score: {good_deals[0]['deal_score']:.1f}" if good_deals else "   - No deals found")
        print(f"\n📁 Output files:")
        print(f"   - Database: data/copart.db")
        print(f"   - Report: {daily_report}")
        print(f"   - Screenshot: logs/search_page.png")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\n⏹  Stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
    finally:
        scraper.stop_browser()


if __name__ == "__main__":
    main()
