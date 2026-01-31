#!/usr/bin/env python3
"""
Test Copart login with saved credentials.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger
from src.scraper import CopartScraper


def test_login():
    """Test login functionality."""
    logger = setup_logger('login_test')

    print("\n" + "="*60)
    print("COPART LOGIN TEST")
    print("="*60)

    # Load credentials from .env
    load_dotenv('config/.env')

    username = os.getenv('COPART_USERNAME')
    password = os.getenv('COPART_PASSWORD')

    if not username or not password:
        print("\n❌ Error: Credentials not found in config/.env")
        print("Please make sure the .env file exists with:")
        print("  COPART_USERNAME=your_email")
        print("  COPART_PASSWORD=your_password")
        return

    print(f"\n✅ Loaded credentials for: {username}")
    print("="*60 + "\n")

    config = Config()

    try:
        # Create scraper with credentials
        logger.info("Creating scraper with stealth mode...")
        scraper = CopartScraper(config, username=username, password=password, use_stealth=True)

        # Start browser
        logger.info("Starting browser...")
        scraper.start_browser()

        # Attempt login
        logger.info("Attempting login...")
        print("\n🔐 Logging in to Copart...")
        print("This may take 10-20 seconds...\n")

        success = scraper.login()

        if success:
            print("\n" + "="*60)
            print("✅ LOGIN SUCCESSFUL!")
            print("="*60)
            print("\n📸 Check logs/after_login.png to see the result")
            print("\nYou can now search for vehicles as a logged-in member!")
        else:
            print("\n" + "="*60)
            print("⚠️  LOGIN FAILED OR UNCERTAIN")
            print("="*60)
            print("\n📸 Check logs/after_login.png to see what happened")
            print("\nPossible issues:")
            print("  1. Incorrect username/password")
            print("  2. Captcha required (needs manual intervention)")
            print("  3. Login page structure changed")
            print("  4. Connection timeout")

        # Cleanup
        logger.info("Cleaning up...")
        scraper.stop_browser()

        print("\n" + "="*60)
        print("Test Complete!")
        print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Test error: {e}", exc_info=True)
        print(f"\n❌ Error during test: {e}")


if __name__ == "__main__":
    test_login()
