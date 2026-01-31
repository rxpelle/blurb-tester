"""
Copart login automation with stealth mode.
"""

import time
import random
from typing import Optional
from playwright.sync_api import Page, BrowserContext

from src.utils import setup_logger
from src.scraper.stealth import apply_stealth_scripts, random_mouse_movement


class CopartLogin:
    """Handle Copart login with stealth."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.logger = setup_logger('copart_login')

    def login(self, page: Page) -> bool:
        """
        Log in to Copart.

        Args:
            page: Playwright page instance

        Returns:
            True if login successful
        """
        try:
            self.logger.info("Starting login process...")

            # Go to Copart homepage
            self.logger.info("Loading Copart homepage...")
            page.goto("https://www.copart.com", timeout=60000)
            time.sleep(random.uniform(2, 4))

            # Look for and click login button
            self.logger.info("Looking for login button...")
            login_clicked = False

            login_selectors = [
                'a[href*="login"]',
                'button:has-text("Log In")',
                'a:has-text("Log In")',
                'a:has-text("Sign In")',
                '[data-uname*="login"]'
            ]

            for selector in login_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        element = page.locator(selector).first
                        if element.is_visible(timeout=2000):
                            element.click()
                            login_clicked = True
                            self.logger.info(f"Clicked login: {selector}")
                            time.sleep(random.uniform(2, 3))
                            break
                except:
                    continue

            if not login_clicked:
                self.logger.warning("Couldn't find login button automatically")
                # Try direct URL
                page.goto("https://www.copart.com/login/", timeout=60000)
                time.sleep(3)

            # Wait for login form
            page.wait_for_timeout(2000)

            # Fill username/email
            self.logger.info("Filling username...")
            username_filled = False

            username_selectors = [
                'input[type="email"]',
                'input[name*="username"]',
                'input[name*="email"]',
                'input[id*="username"]',
                'input[id*="email"]',
                'input[data-uname*="email"]',
                'input[placeholder*="Email"]',
                'input[placeholder*="Username"]'
            ]

            for selector in username_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        # Simulate human typing
                        element.click()
                        time.sleep(random.uniform(0.3, 0.7))

                        for char in self.username:
                            element.type(char, delay=random.randint(50, 150))

                        username_filled = True
                        self.logger.info(f"Filled username with: {selector}")
                        break
                except Exception as e:
                    continue

            if not username_filled:
                self.logger.error("Failed to fill username")
                return False

            time.sleep(random.uniform(0.5, 1.0))

            # Fill password
            self.logger.info("Filling password...")
            password_filled = False

            password_selectors = [
                'input[type="password"]',
                'input[data-uname*="password"]'
            ]

            for selector in password_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        element.click()
                        time.sleep(random.uniform(0.3, 0.7))

                        for char in self.password:
                            element.type(char, delay=random.randint(50, 150))

                        password_filled = True
                        self.logger.info("Filled password")
                        break
                except:
                    continue

            if not password_filled:
                self.logger.error("Failed to fill password")
                return False

            time.sleep(random.uniform(1.0, 2.0))

            # Submit form
            self.logger.info("Submitting login form...")
            submit_clicked = False

            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Sign In")',
                'button:has-text("Log In")',
                'input[type="submit"]',
                'button[data-uname*="login"]',
                'button[class*="submit"]'
            ]

            for selector in submit_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        element.click()
                        submit_clicked = True
                        self.logger.info(f"Clicked submit: {selector}")
                        break
                except:
                    continue

            if not submit_clicked:
                # Try pressing Enter on password field
                page.locator('input[type="password"]').first.press("Enter")
                self.logger.info("Pressed Enter on password field")

            # Wait for login to complete
            self.logger.info("Waiting for login to complete...")
            time.sleep(10)

            # Check if logged in
            current_url = page.url
            self.logger.info(f"Current URL: {current_url}")

            # Take screenshot for verification
            page.screenshot(path="logs/after_login.png")
            self.logger.info("Screenshot saved: logs/after_login.png")

            # Check for successful login indicators
            success_indicators = [
                'a:has-text("My Account")',
                'a:has-text("Logout")',
                'a:has-text("Sign Out")',
                '[data-uname*="logout"]',
                '[href*="logout"]'
            ]

            logged_in = False
            for indicator in success_indicators:
                if page.locator(indicator).count() > 0:
                    logged_in = True
                    self.logger.info(f"✅ Login successful! Found: {indicator}")
                    break

            if not logged_in:
                # Check if we're still on login page
                if 'login' in current_url.lower():
                    self.logger.warning("⚠️ Still on login page - login may have failed")
                    return False
                else:
                    self.logger.info("✅ Login appears successful (redirected from login page)")
                    logged_in = True

            return logged_in

        except Exception as e:
            self.logger.error(f"❌ Login error: {e}", exc_info=True)
            return False
