#!/usr/bin/env python3
"""Test Copart search with actual query."""

import sys
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

sys.path.append(str(Path(__file__).parent))

from src.utils import Config


def test_search():
    """Test searching for Oregon vehicles."""
    print("Testing Copart search for Oregon vehicles...")
    config = Config()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=config.user_agent,
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        try:
            # Navigate to Copart
            print("1. Loading Copart...")
            page.goto("https://www.copart.com", timeout=60000)
            time.sleep(3)

            # Try to search for vehicles
            print("2. Performing search...")

            # Type in search box (look for input field)
            search_input = page.locator('input[type="text"]').first
            if search_input.is_visible(timeout=5000):
                # Search for Toyota in Oregon
                search_input.fill("Toyota")
                time.sleep(1)

                # Press Enter or click search button
                search_input.press("Enter")
                print("   Search submitted!")

            # Wait for results to load
            print("3. Waiting for results...")
            time.sleep(10)  # Give time for dynamic content

            print(f"   Current URL: {page.url}")

            # Take screenshot of results
            page.screenshot(path="logs/copart_search_results.png", full_page=True)
            print("   Screenshot: logs/copart_search_results.png")

            # Save HTML
            html = page.content()
            with open("logs/copart_search_results.html", "w") as f:
                f.write(html)
            print("   HTML: logs/copart_search_results.html")

            # Try to count vehicle cards
            print("\n4. Looking for vehicle elements...")

            # Try various selectors
            selectors = [
                '[data-uname*="lot"]',
                '.vehicle-card',
                '[class*="vehicle"]',
                '[class*="listing"]',
                '[class*="item"]',
                '[data-lot]',
                'li[id^="lot"]',
            ]

            for selector in selectors:
                count = page.locator(selector).count()
                if count > 0:
                    print(f"   ✓ Found {count} elements matching: {selector}")

                    # Get first element HTML
                    if count > 0:
                        first_elem = page.locator(selector).first
                        html_sample = first_elem.evaluate('el => el.outerHTML')
                        print(f"\n   Sample HTML (first 500 chars):")
                        print(f"   {html_sample[:500]}")
                        break

            print("\n5. Test complete!")
            print(f"   Check logs/copart_search_results.png to see what was found")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    test_search()
