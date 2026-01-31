#!/usr/bin/env python3
"""
Search for Oregon vehicles on Copart with location filtering.
"""

import sys
import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger
from src.scraper import CopartScraper
from src.scraper.vehicle_extractor import VehicleExtractor


def search_oregon_vehicles():
    """Search for vehicles in Oregon locations only."""
    logger = setup_logger('search_oregon')

    print("\n" + "="*80)
    print("SEARCHING COPART OREGON VEHICLES")
    print("="*80)

    # Load credentials
    load_dotenv('config/.env')
    username = os.getenv('COPART_USERNAME')
    password = os.getenv('COPART_PASSWORD')

    if not username or not password:
        print("❌ Credentials not found")
        return

    config = Config()
    scraper = CopartScraper(config, username=username, password=password, use_stealth=True)
    extractor = VehicleExtractor()

    try:
        # Start browser
        scraper.start_browser()

        # Login
        print("\n1. Logging in...")
        if not scraper.login():
            print("❌ Login failed")
            return
        print("✅ Logged in successfully")

        # Navigate to Oregon-specific search
        print("\n2. Searching Oregon vehicles...")
        page = scraper.context.new_page()

        # Oregon location IDs based on config
        # Portland North, Portland South, Eugene
        oregon_yards = [
            "portlandnorth",
            "portlandsouth",
            "eugene"
        ]

        # Get target makes from config
        makes = config.get('search', {}).get('makes', ['Honda', 'Toyota', 'Ford', 'Chevrolet'])

        all_vehicles = []

        for make in makes[:2]:  # Start with first 2 makes for testing
            print(f"\n   Searching for {make} vehicles in Oregon...")

            # Build search URL with Oregon location filter
            # Copart search URL structure: /lotSearchResults/?free=true&query={make}&filter={filters}
            search_url = f"https://www.copart.com/lotSearchResults/?free=true&query={make}"

            # Add Oregon state filter
            search_url += "&filter=%7B%22FETI%22:%5B%22OR%22%5D%7D"

            logger.info(f"Navigating to: {search_url}")
            page.goto(search_url, timeout=60000)

            # Wait for results
            print(f"   Waiting for {make} results to load...")
            time.sleep(5)

            # Extract vehicles
            vehicles = extractor.extract_from_page(page)

            # Filter for Oregon only (double-check)
            oregon_vehicles = [v for v in vehicles if v.get('location') and 'OR' in v.get('location', '')]

            print(f"   Found {len(vehicles)} total vehicles, {len(oregon_vehicles)} in Oregon")
            all_vehicles.extend(oregon_vehicles)

            # Save intermediate results
            with open(f'logs/oregon_{make.lower()}_vehicles.json', 'w') as f:
                json.dump(oregon_vehicles, f, indent=2)

            time.sleep(3)  # Rate limiting

        # Save all Oregon vehicles
        print(f"\n3. Saving results...")
        with open('logs/oregon_all_vehicles.json', 'w') as f:
            json.dump(all_vehicles, f, indent=2)

        print(f"\n{'='*80}")
        print(f"SEARCH COMPLETE")
        print(f"{'='*80}")
        print(f"Total Oregon vehicles found: {len(all_vehicles)}")

        # Show summary by location
        locations = {}
        for v in all_vehicles:
            loc = v.get('location', 'Unknown')
            locations[loc] = locations.get(loc, 0) + 1

        print(f"\nBreakdown by location:")
        for loc, count in sorted(locations.items()):
            print(f"  {loc}: {count} vehicles")

        # Show sample vehicles
        if all_vehicles:
            print(f"\nSample vehicles:")
            for i, v in enumerate(all_vehicles[:3], 1):
                print(f"\n  {i}. Lot #{v.get('lot_number')}")
                print(f"     {v.get('year')} {v.get('make')} {v.get('model')}")
                print(f"     Location: {v.get('location')}")
                print(f"     Title: {v.get('title_type')}")

        print(f"\n{'='*80}\n")

        page.close()

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        scraper.stop_browser()


if __name__ == "__main__":
    search_oregon_vehicles()
