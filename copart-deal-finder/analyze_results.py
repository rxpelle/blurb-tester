#!/usr/bin/env python3
"""
Analyze Copart search results to find correct selectors.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import time
import json

sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger
from src.scraper import CopartScraper


def analyze_results():
    """Analyze search results HTML to find selectors."""
    logger = setup_logger('analyze_results')

    print("\n" + "="*60)
    print("ANALYZING COPART SEARCH RESULTS")
    print("="*60)

    # Load credentials
    load_dotenv('config/.env')
    username = os.getenv('COPART_USERNAME')
    password = os.getenv('COPART_PASSWORD')

    if not username or not password:
        print("❌ Credentials not found")
        return

    config = Config()
    scraper = CopartScraper(config, username=username, password=password, use_stealth=True)

    try:
        # Start browser
        scraper.start_browser()

        # Login
        print("\n1. Logging in...")
        if not scraper.login():
            print("❌ Login failed")
            return

        print("✅ Logged in successfully")

        # Navigate to search
        print("\n2. Performing search...")
        page = scraper.context.new_page()

        # Go to search with Toyota query
        page.goto("https://www.copart.com/lotSearchResults/?free=true&query=Toyota", timeout=60000)
        time.sleep(5)

        # Wait for results to load
        print("   Waiting for results to load...")
        time.sleep(5)

        # Save full page HTML
        html = page.content()
        with open("logs/search_results.html", "w") as f:
            f.write(html)
        print("   Saved HTML to: logs/search_results.html")

        # Take screenshot
        page.screenshot(path="logs/search_results_full.png", full_page=True)
        print("   Saved screenshot: logs/search_results_full.png")

        # Try to find vehicle cards
        print("\n3. Looking for vehicle elements...")

        # Try various selectors
        selectors_to_try = [
            'div[data-uname*="lotsearchLotimage"]',
            'li[data-lot]',
            'div[class*="lot-"]',
            'div[class*="vehicle"]',
            'li[id^="serverSideDataTable"]',
            'tr[data-lot-number]',
            'div.lot-details',
            'article',
            'div[ng-repeat*="lot"]',
        ]

        found_selector = None
        for selector in selectors_to_try:
            count = page.locator(selector).count()
            print(f"   {selector}: {count} elements")
            if count > 0 and not found_selector:
                found_selector = selector

        if found_selector:
            print(f"\n✅ Best selector: {found_selector}")

            # Get first element
            first_elem = page.locator(found_selector).first
            elem_html = first_elem.evaluate('el => el.outerHTML')

            # Save sample
            with open("logs/vehicle_card_sample.html", "w") as f:
                f.write(elem_html)
            print(f"   Saved sample HTML to: logs/vehicle_card_sample.html")

            # Try to extract data from first card
            print("\n4. Extracting data from first card...")

            # Try to find data attributes
            all_text = first_elem.text_content()
            print(f"\n   Card text content:\n   {all_text[:500]}")

            # Look for specific data
            data_fields = {
                'lot_number': ['data-lot-number', 'data-lot', 'lot-number'],
                'year': ['data-year'],
                'make': ['data-make'],
                'model': ['data-model'],
                'damage': ['data-damage'],
                'location': ['data-location'],
                'bid': ['data-bid', 'data-current-bid'],
                'value': ['data-value', 'data-retail'],
            }

            print("\n   Looking for data attributes...")
            for field, attrs in data_fields.items():
                for attr in attrs:
                    try:
                        value = first_elem.get_attribute(attr)
                        if value:
                            print(f"   ✓ {field}: {attr} = {value}")
                    except:
                        pass

        else:
            print("\n⚠️  No vehicle cards found with standard selectors")
            print("   The page might use a different structure")

        # Try to find all text that looks like lot numbers
        print("\n5. Looking for lot numbers in page...")
        body_text = page.locator('body').text_content()

        # Save full page text
        with open("logs/page_text.txt", "w") as f:
            f.write(body_text)
        print("   Saved page text to: logs/page_text.txt")

        # Look for patterns
        import re
        lot_numbers = re.findall(r'\b\d{8}\b', body_text)
        if lot_numbers:
            print(f"   Found potential lot numbers: {lot_numbers[:5]}")

        print("\n" + "="*60)
        print("Analysis Complete!")
        print("="*60)
        print("\nCheck these files:")
        print("  - logs/search_results.html")
        print("  - logs/search_results_full.png")
        print("  - logs/vehicle_card_sample.html")
        print("  - logs/page_text.txt")
        print("="*60 + "\n")

        page.close()

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        scraper.stop_browser()


if __name__ == "__main__":
    analyze_results()
