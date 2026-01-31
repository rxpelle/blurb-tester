#!/usr/bin/env python3
"""
Search for actual Oregon vehicles using proper location filtering.
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


def search_actual_oregon():
    """Search for vehicles actually in Oregon."""
    logger = setup_logger('actual_oregon')

    print("\n" + "="*80)
    print("SEARCHING FOR ACTUAL OREGON VEHICLES")
    print("="*80)

    # Load credentials
    load_dotenv('config/.env')
    username = os.getenv('COPART_USERNAME')
    password = os.getenv('COPART_PASSWORD')

    config = Config()
    scraper = CopartScraper(config, username=username, password=password, use_stealth=True)
    extractor = VehicleExtractor()

    try:
        scraper.start_browser()

        print("\n1. Logging in...")
        if not scraper.login():
            print("⚠️  Login failed, continuing...")
        else:
            print("✅ Logged in")

        page = scraper.context.new_page()

        # Try multiple search strategies
        print("\n2. Strategy 1: Search with manual Oregon filter via UI...")

        # Go to main search page
        page.goto("https://www.copart.com/vehicleFinder/", timeout=60000)
        time.sleep(5)

        # Try to interact with location filter
        # (This would require clicking and selecting Oregon from dropdown)
        print("   Note: Manual UI interaction needed for location filter")

        # Strategy 2: Use direct search and filter results by state code
        print("\n3. Strategy 2: Search all vehicles and filter for OR state...")

        all_oregon_vehicles = []
        makes = ['Honda', 'Toyota', 'Ford']

        for make in makes:
            print(f"\n   Searching {make}...")

            search_url = f"https://www.copart.com/lotSearchResults/?free=true&query={make}"
            page.goto(search_url, timeout=60000, wait_until='networkidle')
            time.sleep(8)

            # Extract vehicles
            vehicles = extractor.extract_from_page(page)
            print(f"   Extracted {len(vehicles)} {make} vehicles")

            # Filter for Oregon using STRICT matching
            # Oregon locations should be: "OR - Portland North", "OR - Portland South", "OR - Eugene"
            oregon_only = []
            for v in vehicles:
                loc = v.get('location', '')
                # Must start with "OR -" to be Oregon
                if loc.startswith('OR -'):
                    oregon_only.append(v)
                    print(f"      ✓ Found Oregon: {loc} - Lot #{v['lot_number']}")

            print(f"   → {len(oregon_only)} actual Oregon vehicles")
            all_oregon_vehicles.extend(oregon_only)

            time.sleep(3)

        print(f"\n4. Total actual Oregon vehicles: {len(all_oregon_vehicles)}")

        if not all_oregon_vehicles:
            print("\n⚠️  NO Oregon vehicles found!")
            print("   Possible reasons:")
            print("   - No current inventory at OR auctions for these makes")
            print("   - Oregon auctions may use different location codes")
            print("   - May need member login to see OR inventory")

            # Show what locations we DID find
            print("\n   Let's see what locations were found:")
            page.goto("https://www.copart.com/lotSearchResults/?free=true&query=Honda", timeout=60000)
            time.sleep(8)
            all_vehicles = extractor.extract_from_page(page)

            states = {}
            for v in all_vehicles:
                loc = v.get('location', 'Unknown')
                # Get just the state code
                state = loc.split(' - ')[0] if ' - ' in loc else loc[:2]
                states[state] = states.get(state, 0) + 1

            print(f"\n   States found in Honda search:")
            for state, count in sorted(states.items()):
                print(f"     {state}: {count} vehicles")

        else:
            # Found Oregon vehicles - check which run and drive
            print("\n5. Checking which Oregon vehicles run and drive...")

            runners = []
            for i, vehicle in enumerate(all_oregon_vehicles, 1):
                lot_num = vehicle['lot_number']
                detail_url = vehicle['detail_page_url']

                print(f"\n   [{i}/{len(all_oregon_vehicles)}] Lot {lot_num}...")

                try:
                    detail_page = scraper.context.new_page()
                    detail_page.goto(detail_url, timeout=45000)
                    time.sleep(3)

                    # Check for runs/drives
                    page_text = detail_page.content().lower()
                    runs = 'run and drive' in page_text or 'runs and drives' in page_text

                    if runs:
                        vehicle['runs_drives'] = 'Yes'
                        runners.append(vehicle)
                        print(f"      ✅ RUNS AND DRIVES")
                        print(f"         {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}")
                        print(f"         Location: {vehicle.get('location')}")
                    else:
                        print(f"      ⚠️  Does not run/drive or unknown")

                    detail_page.close()
                    time.sleep(2)

                except Exception as e:
                    logger.warning(f"Error: {e}")

            # Save results
            with open('logs/actual_oregon_all.json', 'w') as f:
                json.dump(all_oregon_vehicles, f, indent=2)

            with open('logs/actual_oregon_runners.json', 'w') as f:
                json.dump(runners, f, indent=2)

            print(f"\n{'='*80}")
            print(f"FINAL RESULTS")
            print(f"{'='*80}")
            print(f"Oregon vehicles found: {len(all_oregon_vehicles)}")
            print(f"Oregon vehicles that RUN & DRIVE: {len(runners)}")

            if runners:
                print(f"\n🚗 OREGON RUNNERS:")
                for v in runners:
                    print(f"\n  📍 Lot #{v['lot_number']}")
                    print(f"     {v.get('year')} {v.get('make')} {v.get('model')}")
                    print(f"     Location: {v.get('location')}")
                    print(f"     Title: {v.get('title_type')}")
                    print(f"     {v.get('detail_page_url')}")

            print(f"\n{'='*80}\n")

        page.close()

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        scraper.stop_browser()


if __name__ == "__main__":
    search_actual_oregon()
