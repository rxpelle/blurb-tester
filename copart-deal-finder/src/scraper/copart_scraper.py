import time
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils import Config, setup_logger
from src.scraper.stealth import StealthConfig, apply_stealth_scripts, random_mouse_movement, human_type
from src.scraper.copart_login import CopartLogin


class CopartScraper:
    """Web scraper for Copart auction listings with stealth mode."""

    def __init__(self, config: Config, username: str = None, password: str = None, use_stealth: bool = True):
        self.config = config
        self.logger = setup_logger('copart_scraper')
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        self.use_stealth = use_stealth
        self.username = username
        self.password = password
        self.logged_in = False

    def start_browser(self):
        """Start Playwright browser with stealth mode."""
        self.logger.info("Starting browser with stealth mode...")
        self.playwright = sync_playwright().start()

        # Stealth browser arguments
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ]

        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=browser_args
        )

        # Create stealth context
        user_agent = StealthConfig.get_random_user_agent()
        viewport = StealthConfig.get_random_viewport()
        timezone = StealthConfig.get_random_timezone()

        self.context = self.browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale="en-US",
            timezone_id=timezone,
            permissions=["geolocation"],
            color_scheme="light",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            }
        )

        self.logger.info(f"Browser started with stealth mode (User-Agent: {user_agent[:50]}...)")

    def stop_browser(self):
        """Stop Playwright browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logger.info("Browser stopped")

    def login(self) -> bool:
        """
        Log in to Copart with member credentials.

        Returns:
            True if login successful
        """
        if not self.username or not self.password:
            self.logger.warning("No credentials provided - skipping login")
            return False

        if self.logged_in:
            self.logger.info("Already logged in")
            return True

        if not self.browser:
            self.start_browser()

        page = self.context.new_page()

        # Apply stealth scripts
        if self.use_stealth:
            apply_stealth_scripts(page)

        # Use login module
        login_handler = CopartLogin(self.username, self.password)
        success = login_handler.login(page)

        page.close()

        self.logged_in = success
        return success

    def search_vehicles(self, location: str = "OR") -> List[Dict[str, Any]]:
        """
        Search for vehicles in Oregon locations.

        Args:
            location: State code (default: OR for Oregon)

        Returns:
            List of vehicle data dictionaries
        """
        self.logger.info(f"Starting vehicle search for location: {location}")

        if not self.browser:
            self.start_browser()

        vehicles = []
        page = self.context.new_page()

        # Apply stealth scripts
        if self.use_stealth:
            apply_stealth_scripts(page)

        try:
            # Navigate to Copart search page
            base_url = "https://www.copart.com"
            self.logger.info(f"Navigating to {base_url}")
            page.goto(base_url, wait_until="domcontentloaded", timeout=60000)

            # Random delay to appear human
            delay = random.uniform(2, 4)
            self.logger.info(f"Waiting {delay:.1f}s (human-like delay)...")
            time.sleep(delay)

            # Simulate mouse movement
            if self.use_stealth:
                random_mouse_movement(page)

            # Apply Oregon filter
            self.logger.info("Applying Oregon location filter...")
            # Note: Actual implementation would need to interact with Copart's UI
            # This is a placeholder for the filtering logic

            # Extract vehicle listings
            vehicles = self._extract_search_results(page)
            self.logger.info(f"Found {len(vehicles)} vehicles in search results")

        except Exception as e:
            self.logger.error(f"Error during search: {e}")
        finally:
            page.close()

        return vehicles

    def _extract_search_results(self, page: Page) -> List[Dict[str, Any]]:
        """Extract vehicle data from search results page."""
        vehicles = []

        try:
            # Wait for results to load
            page.wait_for_selector('.vehicle-card', timeout=10000)

            # Get page content
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Find all vehicle cards
            # Note: Selectors are placeholders - need to inspect actual Copart HTML
            vehicle_cards = soup.find_all('div', class_='vehicle-card')

            for card in vehicle_cards:
                try:
                    vehicle = self._parse_vehicle_card(card)
                    if vehicle:
                        vehicles.append(vehicle)
                except Exception as e:
                    self.logger.warning(f"Error parsing vehicle card: {e}")

        except Exception as e:
            self.logger.error(f"Error extracting search results: {e}")

        return vehicles

    def _parse_vehicle_card(self, card) -> Optional[Dict[str, Any]]:
        """Parse individual vehicle card from search results."""
        # This is a placeholder implementation
        # Actual selectors need to be determined by inspecting Copart's HTML

        try:
            vehicle = {
                'lot_number': None,
                'year': None,
                'make': None,
                'model': None,
                'vin': None,
                'location': None,
                'primary_damage': None,
                'current_bid': 0.0,
                'estimated_retail_value': 0.0,
                'sale_date': None,
                'detail_page_url': None,
                'image_urls': [],
            }

            # Extract data from card
            # Note: These are example selectors that need to be updated
            lot_elem = card.find('span', class_='lot-number')
            if lot_elem:
                vehicle['lot_number'] = int(lot_elem.text.strip())

            return vehicle if vehicle['lot_number'] else None

        except Exception as e:
            self.logger.warning(f"Error parsing vehicle card: {e}")
            return None

    def get_vehicle_details(self, lot_number: int, detail_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific vehicle.

        Args:
            lot_number: Copart lot number
            detail_url: URL to vehicle detail page

        Returns:
            Detailed vehicle data dictionary
        """
        self.logger.info(f"Fetching details for lot {lot_number}")

        if not self.browser:
            self.start_browser()

        page = self.browser.new_page()
        page.set_extra_http_headers({"User-Agent": self.config.user_agent})

        try:
            page.goto(detail_url, wait_until="networkidle", timeout=30000)
            time.sleep(2)

            # Extract detailed information
            vehicle_data = self._extract_vehicle_details(page, lot_number)

            # Rate limiting
            time.sleep(self.config.rate_limit_seconds)

            return vehicle_data

        except Exception as e:
            self.logger.error(f"Error fetching details for lot {lot_number}: {e}")
            return None
        finally:
            page.close()

    def _extract_vehicle_details(self, page: Page, lot_number: int) -> Dict[str, Any]:
        """Extract detailed vehicle information from detail page."""
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Placeholder implementation - actual selectors need to be determined
        vehicle = {
            'lot_number': lot_number,
            'vin': None,
            'year': None,
            'make': None,
            'model': None,
            'trim': None,
            'body_style': None,
            'odometer': None,
            'odometer_status': None,
            'engine_type': None,
            'transmission': None,
            'drivetrain': None,
            'fuel_type': None,
            'title_type': None,
            'title_state': None,
            'primary_damage': None,
            'secondary_damage': None,
            'has_keys': None,
            'runs_drives': None,
            'engine_starts': None,
            'transmission_engages': None,
            'location': None,
            'sale_date': None,
            'sale_type': None,
            'seller': None,
            'current_bid': 0.0,
            'buy_now_price': None,
            'estimated_retail_value': 0.0,
            'reserve_met': False,
            'autograde_score': None,
            'autocheck_score': None,
            'image_urls': [],
            'detail_page_url': page.url,
            'notes': None,
        }

        # Extract data from page
        # This would contain actual parsing logic for Copart's detail page

        return vehicle

    def scrape_oregon_vehicles(self) -> List[Dict[str, Any]]:
        """
        Main method to scrape all Oregon vehicles.

        Returns:
            List of all vehicle data from Oregon locations
        """
        self.logger.info("Starting Oregon vehicle scrape")

        all_vehicles = []

        try:
            self.start_browser()

            # Search for vehicles in Oregon
            search_results = self.search_vehicles(location="OR")

            # Get detailed info for each vehicle
            for idx, vehicle in enumerate(search_results):
                self.logger.info(f"Processing vehicle {idx + 1}/{len(search_results)}")

                if vehicle.get('detail_page_url'):
                    details = self.get_vehicle_details(
                        vehicle['lot_number'],
                        vehicle['detail_page_url']
                    )
                    if details:
                        all_vehicles.append(details)

                # Rate limiting
                time.sleep(self.config.rate_limit_seconds)

            self.logger.info(f"Scraping complete. Found {len(all_vehicles)} vehicles")

        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
        finally:
            self.stop_browser()

        return all_vehicles

    def __enter__(self):
        self.start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_browser()
