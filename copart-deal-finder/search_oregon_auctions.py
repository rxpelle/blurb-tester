#!/usr/bin/env python3
"""
Search for vehicles in upcoming Oregon auctions by location.
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


def search_oregon_auctions():
    """Search upcoming auctions at Oregon locations."""
    logger = setup_logger('oregon_auctions')

    print("\n" + "="*80)
    print("SEARCHING UPCOMING OREGON AUCTIONS")
    print("="*80)

    # Load credentials
    load_dotenv('config/.env')
    username = os.getenv('COPART_USERNAME')
    password = os.getenv('COPART_PASSWORD')

    config = Config()
    scraper = CopartScraper(config, username=username, password=password, use_stealth=True)
    extractor = VehicleExtractor()

    # Oregon Copart locations from config
    oregon_locations = [
        "Portland North",
        "Portland South",
        "Eugene"
    ]

    try:
        scraper.start_browser()

        print("\n1. Logging in...")
        if not scraper.login():
            print("⚠️  Login failed")
            return

        print("✅ Logged in successfully")

        page = scraper.context.new_page()

        all_oregon_vehicles = []

        print("\n2. Searching upcoming auctions at Oregon locations...")

        # Try searching by browsing upcoming auctions
        print("\n   Strategy: Browse by location filter...")

        # Navigate to main search/browse page
        page.goto("https://www.copart.com/vehicleFinder/", timeout=60000)
        time.sleep(5)

        # Save the page to see available filters
        page.screenshot(path='logs/vehiclefinder_page.png')

        # Try the lot search with location-based approach
        # Search for all vehicles and use Copart's location filter in URL
        for location in oregon_locations:
            print(f"\n   Searching {location}...")

            # Try different URL approaches for location filtering
            search_urls = [
                # Approach 1: Use location name in query
                f"https://www.copart.com/lotSearchResults/?free=true&query=&location={location.replace(' ', '+')}",
                # Approach 2: Browse all with location parameter
                f"https://www.copart.com/vehicleFinder/?location={location.replace(' ', '+')}",
            ]

            for url in search_urls[:1]:  # Try first approach
                try:
                    logger.info(f"Trying URL: {url}")
                    page.goto(url, timeout=60000)
                    time.sleep(10)  # Give it time to load with filters

                    # Try to extract vehicles
                    vehicles = extractor.extract_from_page(page)

                    if vehicles:
                        print(f"      Found {len(vehicles)} vehicles")
                        all_oregon_vehicles.extend(vehicles)
                        break
                    else:
                        print(f"      No vehicles found with this URL")

                except Exception as e:
                    logger.warning(f"Error with URL {url}: {e}")
                    continue

            time.sleep(3)

        # Alternative: Try using the advanced search filters interactively
        print("\n   Trying interactive location filter...")
        page.goto("https://www.copart.com/lotSearchResults/?free=true&query=", timeout=60000)
        time.sleep(5)

        # Look for location filter dropdown/controls
        # Check if there's a location filter we can interact with
        try:
            # Try to find and click location filter
            # Common patterns: button, dropdown, filter panel
            filter_selectors = [
                'button:has-text("Location")',
                '[aria-label="Location"]',
                '.location-filter',
                'button:has-text("Filter")',
            ]

            for selector in filter_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        print(f"      Found filter control: {selector}")
                        page.locator(selector).first.click()
                        time.sleep(2)

                        # Save screenshot
                        page.screenshot(path='logs/location_filter_open.png')
                        print(f"      Saved screenshot: logs/location_filter_open.png")
                        break
                except:
                    continue

        except Exception as e:
            logger.warning(f"Could not interact with filters: {e}")

        # Check what we found
        print(f"\n3. Total vehicles found: {len(all_oregon_vehicles)}")

        if not all_oregon_vehicles:
            print("\n⚠️  No vehicles found using location filters")
            print("\n   Let me try a different approach: search by yard number...")

            # Oregon yard IDs (these may need to be looked up)
            # Common Copart yard ID patterns
            yard_attempts = [
                "365",  # Possible Portland North
                "398",  # Possible Portland South
                "512",  # Possible Eugene
            ]

            for yard_id in yard_attempts:
                print(f"\n   Trying yard ID {yard_id}...")
                url = f"https://www.copart.com/lotSearchResults/?free=true&locationId={yard_id}"

                try:
                    page.goto(url, timeout=60000)
                    time.sleep(8)

                    vehicles = extractor.extract_from_page(page)

                    if vehicles:
                        print(f"      ✅ Found {len(vehicles)} vehicles at yard {yard_id}!")
                        all_oregon_vehicles.extend(vehicles)

                        # Save this working approach
                        with open(f'logs/yard_{yard_id}_vehicles.json', 'w') as f:
                            json.dump(vehicles, f, indent=2)
                    else:
                        print(f"      No vehicles at yard {yard_id}")

                except Exception as e:
                    logger.warning(f"Error with yard {yard_id}: {e}")

                time.sleep(3)

        # Process results
        if all_oregon_vehicles:
            print(f"\n{'='*80}")
            print(f"FOUND OREGON AUCTION VEHICLES")
            print(f"{'='*80}")
            print(f"Total vehicles: {len(all_oregon_vehicles)}")

            # Check which run and drive
            print("\n4. Checking which vehicles run and drive...")
            runners = []

            for i, vehicle in enumerate(all_oregon_vehicles[:20], 1):  # Check first 20
                lot_num = vehicle['lot_number']
                detail_url = vehicle['detail_page_url']

                print(f"\n   [{i}/{min(20, len(all_oregon_vehicles))}] Lot {lot_num}...")
                print(f"      {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}")

                try:
                    detail_page = scraper.context.new_page()
                    detail_page.goto(detail_url, timeout=45000)
                    time.sleep(3)

                    # Check for runs/drives
                    page_text = detail_page.content().lower()
                    runs = 'run and drive' in page_text or 'runs and drives' in page_text or 'engine starts' in page_text

                    if runs:
                        vehicle['runs_drives'] = 'Yes'
                        runners.append(vehicle)
                        print(f"      ✅ RUNS AND DRIVES")
                    else:
                        vehicle['runs_drives'] = 'Unknown'
                        print(f"      ⚠️  Runs/drives unknown")

                    detail_page.close()
                    time.sleep(2)

                except Exception as e:
                    logger.warning(f"Error checking lot {lot_num}: {e}")

            # Save results
            with open('logs/oregon_auction_vehicles.json', 'w') as f:
                json.dump(all_oregon_vehicles, f, indent=2)

            with open('logs/oregon_auction_runners.json', 'w') as f:
                json.dump(runners, f, indent=2)

            print(f"\n{'='*80}")
            print(f"FINAL RESULTS")
            print(f"{'='*80}")
            print(f"Oregon auction vehicles: {len(all_oregon_vehicles)}")
            print(f"Vehicles that RUN & DRIVE: {len(runners)}")

            if runners:
                print(f"\n🚗 OREGON RUNNERS:")
                for v in runners:
                    print(f"\n  Lot #{v['lot_number']}")
                    print(f"  {v.get('year')} {v.get('make')} {v.get('model')}")
                    print(f"  Location: {v.get('location')}")
                    print(f"  Title: {v.get('title_type')}")
                    print(f"  {v.get('detail_page_url')}")

            print(f"\nSaved to:")
            print(f"  - logs/oregon_auction_vehicles.json")
            print(f"  - logs/oregon_auction_runners.json")
            print(f"{'='*80}\n")

        else:
            print("\n⚠️  Still no Oregon vehicles found")
            print("   Possible next steps:")
            print("   - Manually check Copart.com for Oregon yard IDs")
            print("   - Look for Oregon auctions in upcoming sales calendar")
            print("   - Contact Copart to verify Oregon locations are active")

        page.close()

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        scraper.stop_browser()


if __name__ == "__main__":
    search_oregon_auctions()
