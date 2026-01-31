"""
Extract vehicle data from Copart search results.

Based on analysis of logged-in member search results.
"""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from playwright.sync_api import Page

from src.utils import setup_logger


class VehicleExtractor:
    """Extract vehicle data from Copart search results."""

    def __init__(self):
        self.logger = setup_logger('vehicle_extractor')

    def extract_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract all vehicles from current search results page.

        Args:
            page: Playwright page with search results loaded

        Returns:
            List of vehicle dictionaries
        """
        vehicles = []

        try:
            # Wait for Angular/React datatable to load
            try:
                page.wait_for_selector('.p-datatable-tbody', timeout=15000)
                self.logger.info("Datatable loaded")
            except:
                self.logger.warning("Datatable not found, continuing anyway...")

            # Copart uses Angular/PrimeNG - extract data from links
            # Each vehicle has a link like: /lot/{lot_number}/{slug}
            lot_links = page.locator('a[href*="/lot/"]').all()
            self.logger.info(f"Found {len(lot_links)} lot links")

            # Track unique lot numbers to avoid duplicates
            seen_lots = set()

            for link in lot_links:
                try:
                    href = link.get_attribute('href')
                    if not href or '/lot/' not in href:
                        continue

                    # Extract lot number from URL
                    parts = href.split('/lot/')
                    if len(parts) < 2:
                        continue

                    lot_parts = parts[1].split('/')
                    if not lot_parts:
                        continue

                    try:
                        lot_number = int(lot_parts[0])
                    except:
                        continue

                    # Skip duplicates
                    if lot_number in seen_lots:
                        continue

                    seen_lots.add(lot_number)

                    # Build full URL
                    detail_url = href if href.startswith('http') else f'https://www.copart.com{href}'

                    # Create vehicle record
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
                        'location': None,
                        'sale_date': None,
                        'current_bid': 0.0,
                        'buy_now_price': None,
                        'estimated_retail_value': 0.0,
                        'autograde_score': None,
                        'detail_page_url': detail_url,
                        'image_urls': [],
                    }

                    # Parse data from URL
                    self._parse_url_data(vehicle)

                    vehicles.append(vehicle)

                except Exception as e:
                    self.logger.warning(f"Error processing link: {e}")
                    continue

            self.logger.info(f"Successfully extracted {len(vehicles)} unique vehicles")

        except Exception as e:
            self.logger.error(f"Error extracting vehicles: {e}")

        return vehicles

    def _extract_vehicle_data(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract vehicle data from a single element.

        Args:
            element: BeautifulSoup element

        Returns:
            Vehicle data dictionary or None
        """
        vehicle = {
            'lot_number': None,
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
            'location': None,
            'sale_date': None,
            'current_bid': 0.0,
            'buy_now_price': None,
            'estimated_retail_value': 0.0,
            'autograde_score': None,
            'detail_page_url': None,
            'image_urls': [],
        }

        # Extract from data attributes (most reliable)
        data_attrs = {
            'lot_number': ['data-lot-number', 'data-lot', 'data-lotnumber'],
            'vin': ['data-vin'],
            'year': ['data-year', 'data-vehicle-year'],
            'make': ['data-make', 'data-vehicle-make'],
            'model': ['data-model', 'data-vehicle-model'],
            'damage': ['data-damage', 'data-primary-damage'],
            'location': ['data-location', 'data-yard'],
            'odometer': ['data-odometer', 'data-miles'],
            'current_bid': ['data-bid', 'data-current-bid'],
            'estimated_retail_value': ['data-value', 'data-retail-value', 'data-estimate'],
        }

        for field, attr_names in data_attrs.items():
            for attr_name in attr_names:
                value = element.get(attr_name)
                if value:
                    # Clean and convert value
                    if field in ['current_bid', 'estimated_retail_value']:
                        try:
                            # Remove currency symbols and commas
                            cleaned = re.sub(r'[^\d.]', '', str(value))
                            vehicle[field if field != 'damage' else 'primary_damage'] = float(cleaned) if cleaned else 0.0
                        except:
                            pass
                    elif field == 'odometer':
                        try:
                            cleaned = re.sub(r'[^\d]', '', str(value))
                            vehicle[field] = int(cleaned) if cleaned else None
                        except:
                            pass
                    elif field == 'lot_number':
                        try:
                            vehicle[field] = int(value)
                        except:
                            vehicle[field] = value
                    else:
                        vehicle[field if field != 'damage' else 'primary_damage'] = str(value).strip()
                    break

        # Extract from text content if data attributes not available
        text = element.get_text()

        # Try to find lot number in text (8 digits)
        if not vehicle['lot_number']:
            lot_match = re.search(r'\b(\d{8})\b', text)
            if lot_match:
                vehicle['lot_number'] = int(lot_match.group(1))

        # Try to find year (4 digits, 19xx or 20xx)
        if not vehicle['year']:
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
            if year_match:
                vehicle['year'] = int(year_match.group(1))

        # Try to find prices (currency format)
        if not vehicle['current_bid']:
            bid_match = re.search(r'\$\s*([\d,]+)', text)
            if bid_match:
                try:
                    vehicle['current_bid'] = float(bid_match.group(1).replace(',', ''))
                except:
                    pass

        # Extract links
        links = element.find_all('a', href=True)
        for link in links:
            href = link['href']
            if '/lot/' in href or 'lotdetails' in href.lower():
                if not href.startswith('http'):
                    href = 'https://www.copart.com' + href
                vehicle['detail_page_url'] = href

        # Extract images
        images = element.find_all('img', src=True)
        image_urls = []
        for img in images:
            src = img['src']
            if 'copart' in src or 'vehicle' in src.lower():
                image_urls.append(src)
        vehicle['image_urls'] = image_urls

        # Parse additional data from detail_page_url if available
        if vehicle['detail_page_url']:
            self._parse_url_data(vehicle)

        return vehicle if vehicle['lot_number'] else None

    def _parse_url_data(self, vehicle: Dict[str, Any]) -> None:
        """
        Parse make, model, year, title, and location from detail page URL.

        Example URL:
        https://www.copart.com/lot/97313745/clean-title-2025-toyota-tacoma-double-cab-ny-buffalo

        Args:
            vehicle: Vehicle dictionary to update
        """
        url = vehicle['detail_page_url']

        try:
            # Extract the path after /lot/
            # Format: /lot/{lot_number}/{title-type}-{year}-{make}-{model}-{location}
            parts = url.split('/lot/')
            if len(parts) < 2:
                return

            # Get the path after lot number
            path_parts = parts[1].split('/', 1)
            if len(path_parts) < 2:
                return

            slug = path_parts[1]

            # Split by hyphens
            slug_parts = slug.split('-')

            if len(slug_parts) < 4:
                return

            # First part is typically title type (e.g., "clean", "salvage")
            if not vehicle['title_type']:
                title_type = slug_parts[0].replace('_', ' ').title()
                if title_type in ['Clean', 'Salvage', 'Rebuilt', 'Parts', 'Lien']:
                    vehicle['title_type'] = title_type

            # Look for year (4-digit number starting with 19 or 20)
            year_idx = None
            for i, part in enumerate(slug_parts):
                if part.isdigit() and len(part) == 4 and part.startswith(('19', '20')):
                    if not vehicle['year']:
                        vehicle['year'] = int(part)
                    year_idx = i
                    break

            # Make and model come after year
            if year_idx is not None and year_idx + 1 < len(slug_parts):
                # Make is right after year
                if not vehicle['make']:
                    vehicle['make'] = slug_parts[year_idx + 1].title()

                # Find state code (2 letters, usually uppercase in original URL)
                state_idx = None
                for i in range(year_idx + 2, len(slug_parts)):
                    part = slug_parts[i]
                    # State code is exactly 2 letters
                    if len(part) == 2 and part.isalpha():
                        state_idx = i
                        break

                # Model is everything between make and state code
                if state_idx is not None:
                    model_parts = slug_parts[year_idx + 2:state_idx]
                    if model_parts and not vehicle['model']:
                        vehicle['model'] = ' '.join([p.title() for p in model_parts])

                    # Location is state code and everything after
                    if not vehicle['location']:
                        location_parts = slug_parts[state_idx:]
                        # Format: "TX - Dallas South"
                        state = location_parts[0].upper()
                        city = ' '.join([p.title() for p in location_parts[1:]]) if len(location_parts) > 1 else ''
                        vehicle['location'] = f"{state} - {city}" if city else state
                else:
                    # No state code found, treat everything as model
                    model_parts = slug_parts[year_idx + 2:]
                    if model_parts and not vehicle['model']:
                        vehicle['model'] = ' '.join([p.title() for p in model_parts])

        except Exception as e:
            self.logger.warning(f"Error parsing URL data: {e}")

    def extract_from_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Extract vehicles from HTML string.

        Args:
            html: HTML content

        Returns:
            List of vehicle dictionaries
        """
        vehicles = []

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Similar extraction logic as extract_from_page
            # but working directly with HTML string

            elements_with_lot = soup.find_all(attrs={'data-lot-number': True})

            for element in elements_with_lot:
                vehicle = self._extract_vehicle_data(element)
                if vehicle:
                    vehicles.append(vehicle)

            self.logger.info(f"Extracted {len(vehicles)} vehicles from HTML")

        except Exception as e:
            self.logger.error(f"Error extracting from HTML: {e}")

        return vehicles
