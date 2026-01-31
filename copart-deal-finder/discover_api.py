#!/usr/bin/env python3
"""
Discover Copart API endpoints by analyzing network traffic.

This script will:
1. Log in to Copart with your credentials
2. Monitor network requests
3. Identify API endpoints
4. Save API documentation
"""

import sys
from pathlib import Path
import time
import json
from playwright.sync_api import sync_playwright

sys.path.append(str(Path(__file__).parent))

from src.utils import Config, setup_logger
from src.scraper.stealth import apply_stealth_scripts, StealthConfig


def discover_api():
    """Discover Copart API endpoints."""
    logger = setup_logger('api_discovery')

    print("\n" + "="*60)
    print("COPART API DISCOVERY TOOL")
    print("="*60)
    print("\nThis will help you find Copart's API endpoints.")
    print("You'll need to log in with your Copart credentials.")
    print("\nPress Ctrl+C at any time to stop.\n")

    # Get credentials
    print("Enter your Copart login credentials:")
    username = input("Username/Email: ").strip()

    if not username:
        print("❌ Username required!")
        return

    import getpass
    password = getpass.getpass("Password: ")

    if not password:
        print("❌ Password required!")
        return

    print("\n" + "="*60)
    print("Starting API discovery...")
    print("="*60 + "\n")

    config = Config()
    api_calls = []

    with sync_playwright() as playwright:
        # Launch browser
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ]

        browser = playwright.chromium.launch(
            headless=False,  # Visible so you can see what's happening
            args=browser_args
        )

        # Create context with stealth
        user_agent = StealthConfig.get_random_user_agent()
        viewport = StealthConfig.get_random_viewport()

        context = browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale="en-US",
        )

        page = context.new_page()
        apply_stealth_scripts(page)

        # Monitor network requests
        def handle_request(request):
            url = request.url
            method = request.method

            # Look for API calls
            if any(keyword in url.lower() for keyword in ['api', 'json', 'graphql', 'rest', 'ajax']):
                api_calls.append({
                    'method': method,
                    'url': url,
                    'headers': request.headers,
                    'post_data': request.post_data if method == 'POST' else None
                })
                print(f"📡 API Call: {method} {url[:80]}...")

        def handle_response(response):
            url = response.url

            # Look for JSON responses
            if 'application/json' in response.headers.get('content-type', ''):
                try:
                    # Save response
                    for api_call in api_calls:
                        if api_call['url'] == url:
                            api_call['response_status'] = response.status
                            api_call['response_headers'] = response.headers
                            print(f"   ↳ Status: {response.status}")
                except:
                    pass

        page.on('request', handle_request)
        page.on('response', handle_response)

        try:
            # Navigate to Copart
            logger.info("1. Loading Copart...")
            page.goto("https://www.copart.com", timeout=60000)
            time.sleep(2)

            # Find and click login
            logger.info("2. Looking for login button...")
            try:
                # Try to find login link/button
                login_selectors = [
                    'a[href*="login"]',
                    'button:has-text("Log In")',
                    'a:has-text("Log In")',
                    'a:has-text("Sign In")',
                ]

                for selector in login_selectors:
                    if page.locator(selector).count() > 0:
                        logger.info(f"   Found login with selector: {selector}")
                        page.locator(selector).first.click()
                        time.sleep(2)
                        break

            except Exception as e:
                logger.warning(f"Couldn't auto-click login: {e}")
                print("\n⚠️  Please click the login button manually in the browser...")
                time.sleep(5)

            # Fill in login form
            logger.info("3. Filling login form...")
            try:
                # Look for username/email field
                username_selectors = [
                    'input[type="email"]',
                    'input[name*="username"]',
                    'input[name*="email"]',
                    'input[id*="username"]',
                    'input[id*="email"]',
                ]

                for selector in username_selectors:
                    if page.locator(selector).count() > 0:
                        logger.info(f"   Found username field: {selector}")
                        page.locator(selector).first.fill(username)
                        break

                # Look for password field
                password_field = page.locator('input[type="password"]').first
                password_field.fill(password)

                time.sleep(1)

                # Submit form
                submit_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Sign In")',
                    'button:has-text("Log In")',
                    'input[type="submit"]',
                ]

                for selector in submit_selectors:
                    if page.locator(selector).count() > 0:
                        logger.info(f"   Clicking submit: {selector}")
                        page.locator(selector).first.click()
                        break

            except Exception as e:
                logger.warning(f"Auto-fill failed: {e}")
                print("\n⚠️  Please log in manually in the browser...")

            # Wait for login
            logger.info("4. Waiting for login to complete...")
            time.sleep(10)

            # Navigate to search
            logger.info("5. Navigating to vehicle search...")
            page.goto("https://www.copart.com/vehicleFinder/", timeout=60000)
            time.sleep(5)

            # Interact with search to trigger API calls
            logger.info("6. Interacting with search (this triggers API calls)...")

            # Type in search box to trigger autocomplete/search APIs
            try:
                search_input = page.locator('input[type="text"]').first
                if search_input.is_visible():
                    search_input.fill("Toyota")
                    time.sleep(3)
                    search_input.press("Enter")
                    time.sleep(5)
            except:
                pass

            # Scroll page to trigger lazy loading
            logger.info("7. Scrolling to trigger more API calls...")
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 500)")
                time.sleep(2)

            print("\n" + "="*60)
            print(f"✅ Discovery complete! Found {len(api_calls)} API calls")
            print("="*60)

            # Save results
            output_file = "logs/copart_api_calls.json"
            with open(output_file, 'w') as f:
                json.dump(api_calls, f, indent=2)

            print(f"\n📝 API calls saved to: {output_file}")

            # Show summary
            print("\n📊 API SUMMARY:")
            print("-"*60)

            unique_endpoints = set()
            for call in api_calls:
                # Extract base endpoint
                url = call['url']
                if '?' in url:
                    url = url.split('?')[0]
                unique_endpoints.add(url)

            for endpoint in sorted(unique_endpoints):
                print(f"  • {endpoint}")

            print("\n💡 TIPS:")
            print("  1. Check logs/copart_api_calls.json for full details")
            print("  2. Look for endpoints with 'search', 'vehicle', 'lot'")
            print("  3. Note the authentication headers used")
            print("  4. Check request/response formats")

            print("\n⏸  Browser will stay open for manual inspection.")
            print("   Press Enter when done to close...")
            input()

        except KeyboardInterrupt:
            print("\n\n⏹  Stopped by user")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
        finally:
            browser.close()


if __name__ == "__main__":
    discover_api()
