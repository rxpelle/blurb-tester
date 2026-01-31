#!/usr/bin/env python3
"""
Test waiting for Angular app to fully load vehicle data.
"""

import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger
from src.scraper import CopartScraper
from src.scraper.vehicle_extractor import VehicleExtractor

load_dotenv('config/.env')
username = os.getenv('COPART_USERNAME')
password = os.getenv('COPART_PASSWORD')

config = Config()
scraper = CopartScraper(config, username=username, password=password, use_stealth=True)
extractor = VehicleExtractor()

scraper.start_browser()
scraper.login()

page = scraper.context.new_page()

# Try Toyota search
print("\n1. Loading Toyota search page...")
search_url = 'https://www.copart.com/lotSearchResults/?free=true&query=Toyota'
page.goto(search_url, timeout=60000, wait_until='networkidle')

print("   Waiting for Angular to load...")
time.sleep(10)  # Give Angular more time to render

# Wait for specific Angular/PrimeNG elements
try:
    # Wait for the datatable to be present
    page.wait_for_selector('.p-datatable-tbody', timeout=15000)
    print("   ✅ Datatable loaded")
except:
    print("   ⚠️  Datatable not found")

# Try to find lot number elements
print("\n2. Looking for lot numbers...")
selectors_to_try = [
    'a[href*="/lot/"]',  # Links to lot detail pages
    '.search_result_lot_number',
    '[class*="lot"]',
    'td',  # Table cells
]

for selector in selectors_to_try:
    count = page.locator(selector).count()
    print(f"   {selector}: {count} elements")
    if count > 0 and count < 100:  # Reasonable number
        first_text = page.locator(selector).first.text_content()
        print(f"      First element text: {first_text[:100] if first_text else '(empty)'}...")

# Get all links that contain '/lot/'
lot_links = page.locator('a[href*="/lot/"]').all()
print(f"\n3. Found {len(lot_links)} lot links")

if lot_links:
    print("   First 3 lot links:")
    for i, link in enumerate(lot_links[:3], 1):
        href = link.get_attribute('href')
        text = link.text_content()
        print(f"   {i}. {href} - Text: {text}")

# Save this attempt
page.screenshot(path='logs/angular_loaded.png', full_page=True)
with open('logs/angular_loaded.html', 'w') as f:
    f.write(page.content())

print("\n4. Saved:")
print("   - logs/angular_loaded.png")
print("   - logs/angular_loaded.html")

page.close()
scraper.stop_browser()
