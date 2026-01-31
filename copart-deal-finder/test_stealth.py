#!/usr/bin/env python3
"""Test stealth mode scraper against Copart."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger
from src.scraper import CopartScraper


def test_stealth():
    """Test stealth scraper."""
    logger = setup_logger('stealth_test')
    logger.info("="*60)
    logger.info("Testing Copart Scraper with Stealth Mode")
    logger.info("="*60)

    config = Config()

    try:
        # Create scraper with stealth mode
        scraper = CopartScraper(config, use_stealth=True)

        logger.info("\n[1/3] Starting stealth browser...")
        scraper.start_browser()

        logger.info("\n[2/3] Attempting to access Copart...")
        logger.info("This will test if stealth mode bypasses bot detection...")

        # Try to get some vehicles
        vehicles = scraper.search_vehicles(location="OR")

        if vehicles:
            logger.info(f"\n✅ SUCCESS! Found {len(vehicles)} vehicles")
            logger.info("Stealth mode appears to be working!")
        else:
            logger.warning("\n⚠️  No vehicles found, but no blocking error!")
            logger.info("This might mean:")
            logger.info("  1. Stealth mode worked but search needs refinement")
            logger.info("  2. Bot detection was bypassed")
            logger.info("  3. No results for the search criteria")

        logger.info("\n[3/3] Cleaning up...")
        scraper.stop_browser()

        logger.info("\n" + "="*60)
        logger.info("Test Complete!")
        logger.info("Check logs/ directory for screenshots and HTML")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
        logger.info("\nIf you see 'Access denied' or 'Error 15':")
        logger.info("  - Bot detection is still catching us")
        logger.info("  - May need residential proxy or more advanced stealth")
        logger.info("\nIf you see other errors:")
        logger.info("  - Check the error message for details")
        logger.info("  - May need to update selectors or wait times")


if __name__ == "__main__":
    test_stealth()
