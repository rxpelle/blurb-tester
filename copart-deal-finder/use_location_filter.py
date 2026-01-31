#!/usr/bin/env python3
"""
Use Copart's actual location filter to find Oregon vehicles.
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


def use_location_filter():
    """Use the proper location filter on Vehicle Finder page."""
    logger = setup_logger('location_filter')

    print("\n" + "="*80)
    print("USING COPART LOCATION FILTER FOR OREGON")
    print("="*80)

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
            print("⚠️  Login failed")
            return

        print("✅ Logged in")

        page = scraper.context.new_page()

        print("\n2. Opening Vehicle Finder...")
        page.goto("https://www.copart.com/vehicleFinder/", timeout=60000)
        time.sleep(5)

        print("\n3. Interacting with Location filter...")

        # Click on the "All Locations" dropdown
        try:
            # Find and click the location dropdown
            dropdown_selectors = [
                'select:has-text("All Locations")',
                '[id*="location"]',
                'select[name*="location"]',
                '.location-select',
            ]

            clicked = False
            for selector in dropdown_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        print(f"   Found dropdown: {selector} ({count} elements)")
                        page.locator(selector).first.click()
                        clicked = True
                        time.sleep(2)
                        break
                except:
                    continue

            if not clicked:
                print("   Trying to find dropdown by text...")
                # Try clicking the dropdown text
                page.click('text="All Locations"')
                time.sleep(2)

            # Take screenshot of dropdown
            page.screenshot(path='logs/location_dropdown.png')
            print("   Screenshot saved: logs/location_dropdown.png")

            # Try to select Oregon locations
            oregon_searches = [
                "Portland North",
                "Portland South",
                "Eugene",
                "OR - Portland",
                "OR - Eugene",
            ]

            all_oregon_vehicles = []

            for location_name in oregon_searches:
                print(f"\n   Trying to select: {location_name}...")

                try:
                    # Try to find and select the option
                    option_found = False

                    # Method 1: Use select dropdown
                    try:
                        page.select_option('select', label=location_name)
                        option_found = True
                        print(f"      ✓ Selected via dropdown")
                    except:
                        pass

                    # Method 2: Type in search box if there's an autocomplete
                    if not option_found:
                        try:
                            page.fill('input[placeholder*="location"]', location_name)
                            time.sleep(1)
                            page.press('input[placeholder*="location"]', 'Enter')
                            option_found = True
                            print(f"      ✓ Entered via search")
                        except:
                            pass

                    if option_found:
                        # Wait for results to load
                        time.sleep(5)

                        # Click "Search Inventory" or submit button
                        submit_buttons = [
                            'button:has-text("Search")',
                            'button:has-text("Submit")',
                            'input[type="submit"]',
                        ]

                        for btn in submit_buttons:
                            try:
                                if page.locator(btn).count() > 0:
                                    page.locator(btn).first.click()
                                    print(f"      Clicked submit button")
                                    break
                            except:
                                continue

                        time.sleep(8)

                        # Extract vehicles
                        vehicles = extractor.extract_from_page(page)

                        if vehicles:
                            print(f"      ✅ Found {len(vehicles)} vehicles!")
                            all_oregon_vehicles.extend(vehicles)

                            # Save these
                            with open(f'logs/{location_name.replace(" ", "_")}_vehicles.json', 'w') as f:
                                json.dump(vehicles, f, indent=2)

                        # Go back to filter page for next location
                        page.goto("https://www.copart.com/vehicleFinder/", timeout=60000)
                        time.sleep(3)

                except Exception as e:
                    logger.warning(f"Error selecting {location_name}: {e}")
                    continue

            if all_oregon_vehicles:
                # Filter for actual Oregon
                actual_oregon = [v for v in all_oregon_vehicles if v.get('location', '').startswith('OR -')]

                print(f"\n{'='*80}")
                print(f"RESULTS")
                print(f"{'='*80}")
                print(f"Total vehicles found: {len(all_oregon_vehicles)}")
                print(f"Actual Oregon vehicles: {len(actual_oregon)}")

                if actual_oregon:
                    print("\n✅ FOUND OREGON VEHICLES!")
                    for v in actual_oregon[:10]:
                        print(f"\n  Lot #{v['lot_number']}")
                        print(f"  {v.get('year')} {v.get('make')} {v.get('model')}")
                        print(f"  Location: {v.get('location')}")

                    # Save
                    with open('logs/actual_oregon_from_filter.json', 'w') as f:
                        json.dump(actual_oregon, f, indent=2)

            else:
                print("\n⚠️  No vehicles found using location filter")

        except Exception as e:
            logger.error(f"Error using location filter: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")

        page.close()

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        scraper.stop_browser()


if __name__ == "__main__":
    use_location_filter()
