#!/usr/bin/env python3
"""
Test script to explore Copart website structure and extract real data.
"""

import sys
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger


def explore_copart():
    """Explore Copart website to understand structure."""
    logger = setup_logger('copart_explorer')
    config = Config()

    logger.info("Starting Copart website exploration...")

    with sync_playwright() as playwright:
        # Launch browser in visible mode to see what's happening
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=config.user_agent,
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        try:
            # Navigate to Copart
            logger.info("Navigating to Copart.com...")
            page.goto("https://www.copart.com", wait_until="networkidle", timeout=60000)

            logger.info("Page loaded. Waiting 3 seconds...")
            time.sleep(3)

            # Try to navigate to vehicle search
            logger.info("Looking for search/browse options...")

            # Save screenshot
            screenshot_path = "logs/copart_homepage.png"
            page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")

            # Try to find and click on vehicle search/browse
            try:
                # Look for common search elements
                search_button = page.locator('text=/Find.*Vehicle|Search|Browse/i').first
                if search_button.is_visible(timeout=5000):
                    logger.info("Found search button, clicking...")
                    search_button.click()
                    time.sleep(3)
                    page.screenshot(path="logs/copart_search.png")
            except:
                logger.warning("Could not automatically navigate to search")

            # Get page content and save for analysis
            html_content = page.content()
            with open("logs/copart_page.html", "w") as f:
                f.write(html_content)
            logger.info("Page HTML saved to logs/copart_page.html")

            # Try to find vehicle listings
            logger.info("Analyzing page structure...")

            # Print URL
            logger.info(f"Current URL: {page.url}")

            # Keep browser open for manual inspection
            logger.info("\n" + "="*60)
            logger.info("Browser is open for manual inspection.")
            logger.info("You can:")
            logger.info("1. Navigate to the vehicle search manually")
            logger.info("2. Inspect the HTML elements")
            logger.info("3. Note the selectors for vehicle cards")
            logger.info("="*60)
            logger.info("\nPress Enter when done to close the browser...")
            input()

        except Exception as e:
            logger.error(f"Error exploring Copart: {e}", exc_info=True)
        finally:
            browser.close()
            logger.info("Browser closed")


if __name__ == "__main__":
    explore_copart()
