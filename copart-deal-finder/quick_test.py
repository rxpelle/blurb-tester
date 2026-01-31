#!/usr/bin/env python3
"""Quick test to fetch Copart data."""

import sys
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

sys.path.append(str(Path(__file__).parent))

from src.utils import Config


def quick_test():
    """Quick automated test of Copart."""
    print("Starting Copart quick test...")
    config = Config()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(user_agent=config.user_agent)
        page = context.new_page()

        try:
            # Navigate to Copart search
            print("Loading Copart vehicle search...")
            page.goto("https://www.copart.com/vehicleFinder/", timeout=60000)

            time.sleep(5)

            print(f"Page loaded: {page.title()}")
            print(f"URL: {page.url}")

            # Take screenshot
            page.screenshot(path="logs/copart_test.png")
            print("Screenshot saved to logs/copart_test.png")

            # Save HTML
            html = page.content()
            with open("logs/copart_test.html", "w") as f:
                f.write(html)
            print("HTML saved to logs/copart_test.html")

            # Try to find some elements
            print("\nLooking for vehicle elements...")

            # Check for any divs or cards that might be vehicles
            cards = page.locator('[data-uname*="lot"], .vehicle-card, [class*="vehicle"], [class*="listing"]').count()
            print(f"Found {cards} potential vehicle elements")

            # Get page text content sample
            body_text = page.locator('body').text_content()[:500]
            print(f"\nPage text sample:\n{body_text}")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
            print("\nTest complete!")


if __name__ == "__main__":
    quick_test()
