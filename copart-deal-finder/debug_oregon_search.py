#!/usr/bin/env python3
"""
Debug Oregon search to see actual page structure.
"""

import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger
from src.scraper import CopartScraper

load_dotenv('config/.env')
username = os.getenv('COPART_USERNAME')
password = os.getenv('COPART_PASSWORD')

config = Config()
scraper = CopartScraper(config, username=username, password=password, use_stealth=True)

scraper.start_browser()
scraper.login()

page = scraper.context.new_page()

# Try Oregon search
print("\n1. Testing Oregon Toyota search...")
search_url = 'https://www.copart.com/lotSearchResults/?free=true&query=Toyota&filter={%22FETI%22:[%22OR%22]}'
page.goto(search_url, timeout=60000)
time.sleep(8)  # Give it more time to load

# Save HTML
html = page.content()
with open('logs/oregon_search_page.html', 'w') as f:
    f.write(html)
print("   Saved HTML: logs/oregon_search_page.html")

# Take screenshot
page.screenshot(path='logs/oregon_search_page.png', full_page=True)
print("   Saved screenshot: logs/oregon_search_page.png")

# Check for "no results" message
body_text = page.locator('body').text_content()
if 'no result' in body_text.lower() or 'no vehicle' in body_text.lower():
    print("   ⚠️  Page shows 'no results' message")
else:
    print(f"   Page loaded, checking for vehicles...")

# Try to count visible vehicles
try:
    vehicle_count = page.locator('[data-uname*="lotsearchLotimage"]').count()
    print(f"   Found {vehicle_count} vehicle image elements")
except:
    print("   Could not count vehicle elements")

# Try without filter
print("\n2. Testing Toyota search WITHOUT Oregon filter...")
search_url_no_filter = 'https://www.copart.com/lotSearchResults/?free=true&query=Toyota'
page.goto(search_url_no_filter, timeout=60000)
time.sleep(8)

# Save this too
with open('logs/all_toyota_search_page.html', 'w') as f:
    f.write(page.content())
page.screenshot(path='logs/all_toyota_search_page.png', full_page=True)

vehicle_count = page.locator('[data-uname*="lotsearchLotimage"]').count()
print(f"   Found {vehicle_count} vehicle image elements without filter")

print("\n3. Testing search with manual Oregon yard selection...")
# Try using specific yard IDs
page.goto('https://www.copart.com/', timeout=60000)
time.sleep(3)

# Click on search/browse
# This would require more interactive automation
print("   Manual yard selection would require UI automation")

page.close()
scraper.stop_browser()

print("\nCheck these files:")
print("  - logs/oregon_search_page.html")
print("  - logs/oregon_search_page.png")
print("  - logs/all_toyota_search_page.html")
print("  - logs/all_toyota_search_page.png")
