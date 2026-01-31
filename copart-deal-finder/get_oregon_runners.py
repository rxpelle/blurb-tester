#!/usr/bin/env python3
"""
Get Oregon vehicles that run and drive.
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


def get_oregon_runners():
    """Search for Oregon vehicles that run and drive."""
    logger = setup_logger('oregon_runners')

    print("\n" + "="*80)
    print("SEARCHING OREGON VEHICLES THAT RUN & DRIVE")
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
            print("⚠️  Login failed, continuing without login...")
        else:
            print("✅ Logged in successfully")

        print("\n2. Searching for vehicles in Oregon...")
        page = scraper.context.new_page()

        all_oregon_vehicles = []

        # Get target makes from config
        makes = config.get('search', {}).get('makes', ['Honda', 'Toyota', 'Ford', 'Chevrolet'])

        for make in makes[:3]:  # Search first 3 makes
            print(f"\n   Searching {make}...")

            # Build comprehensive search URL
            # Search for make in Oregon with runs/drives filter
            search_url = (
                f"https://www.copart.com/lotSearchResults/"
                f"?free=true&query={make}"
                # Note: We'll filter location and runs/drives in the extracted data
            )

            logger.info(f"Loading search: {search_url}")
            page.goto(search_url, timeout=60000, wait_until='networkidle')

            # Wait for page to fully load
            time.sleep(8)

            # Extract vehicles
            vehicles = extractor.extract_from_page(page)
            print(f"   Found {len(vehicles)} {make} vehicles total")

            # Filter for Oregon
            oregon_vehicles = [v for v in vehicles if v.get('location') and 'OR' in v.get('location', '').upper()]
            print(f"   → {len(oregon_vehicles)} in Oregon")

            all_oregon_vehicles.extend(oregon_vehicles)

            time.sleep(3)  # Rate limiting

        print(f"\n3. Total Oregon vehicles found: {len(all_oregon_vehicles)}")

        if not all_oregon_vehicles:
            print("\n⚠️  No Oregon vehicles found in search results.")
            print("   This could mean:")
            print("   - No vehicles currently at OR auctions for these makes")
            print("   - Location filter needs adjustment")
            print("   - Need to visit detail pages to confirm location")

            # Save all vehicles for analysis
            page.goto("https://www.copart.com/lotSearchResults/?free=true&query=Honda", timeout=60000)
            time.sleep(8)
            all_vehicles = extractor.extract_from_page(page)

            print(f"\n   Checking all {len(all_vehicles)} Honda vehicles for Oregon...")
            locations = {}
            for v in all_vehicles:
                loc = v.get('location', 'Unknown')
                locations[loc] = locations.get(loc, 0) + 1

            print("\n   Location breakdown:")
            for loc, count in sorted(locations.items()):
                print(f"     {loc}: {count}")

            with open('logs/all_honda_vehicles.json', 'w') as f:
                json.dump(all_vehicles, f, indent=2)
            print("\n   Saved all vehicles to: logs/all_honda_vehicles.json")

        else:
            # We have Oregon vehicles - now need to visit detail pages to check runs/drives
            print("\n4. Checking which vehicles run and drive...")
            print("   (Need to visit detail pages for this information)")

            runners = []

            for i, vehicle in enumerate(all_oregon_vehicles[:10], 1):  # Test with first 10
                lot_num = vehicle['lot_number']
                detail_url = vehicle['detail_page_url']

                print(f"\n   [{i}/{min(10, len(all_oregon_vehicles))}] Checking lot {lot_num}...")

                try:
                    # Visit detail page
                    detail_page = scraper.context.new_page()
                    detail_page.goto(detail_url, timeout=45000)
                    time.sleep(3)

                    # Look for "Runs and Drives" indicator
                    # Common selectors: text containing "run", "drive", "starts", etc.
                    page_text = detail_page.content().lower()

                    # Check for positive indicators
                    runs = 'run and drive' in page_text or 'runs and drives' in page_text or 'starts' in page_text

                    if runs:
                        vehicle['runs_drives'] = 'Yes'
                        runners.append(vehicle)
                        print(f"      ✅ Runs and drives!")
                    else:
                        vehicle['runs_drives'] = 'Unknown'
                        print(f"      ⚠️  Runs/drives status unknown")

                    detail_page.close()
                    time.sleep(2)  # Rate limiting

                except Exception as e:
                    logger.warning(f"Error checking lot {lot_num}: {e}")
                    print(f"      ❌ Error checking detail page")

            # Save results
            with open('logs/oregon_vehicles_all.json', 'w') as f:
                json.dump(all_oregon_vehicles, f, indent=2)

            with open('logs/oregon_runners.json', 'w') as f:
                json.dump(runners, f, indent=2)

            print(f"\n{'='*80}")
            print(f"RESULTS")
            print(f"{'='*80}")
            print(f"Total Oregon vehicles: {len(all_oregon_vehicles)}")
            print(f"Vehicles that run & drive: {len(runners)}")

            if runners:
                print(f"\nOregon Runners:")
                for v in runners:
                    print(f"\n  Lot #{v['lot_number']}")
                    print(f"  {v.get('year')} {v.get('make')} {v.get('model')}")
                    print(f"  Location: {v.get('location')}")
                    print(f"  Title: {v.get('title_type')}")
                    print(f"  URL: {v.get('detail_page_url')}")

            print(f"\nSaved to:")
            print(f"  - logs/oregon_vehicles_all.json")
            print(f"  - logs/oregon_runners.json")
            print(f"{'='*80}\n")

        page.close()

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
    finally:
        scraper.stop_browser()


if __name__ == "__main__":
    get_oregon_runners()
