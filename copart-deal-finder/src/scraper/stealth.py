"""
Stealth techniques to bypass bot detection.
"""

import random
from typing import Dict, Any
from playwright.sync_api import BrowserContext, Page


class StealthConfig:
    """Configuration for stealth browsing."""

    # Rotate between different user agents
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    # Common viewport sizes
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
    ]

    # Browser languages
    LANGUAGES = ["en-US", "en"]

    # Timezones
    TIMEZONES = ["America/New_York", "America/Chicago", "America/Los_Angeles"]

    @classmethod
    def get_random_user_agent(cls) -> str:
        """Get a random user agent."""
        return random.choice(cls.USER_AGENTS)

    @classmethod
    def get_random_viewport(cls) -> Dict[str, int]:
        """Get a random viewport size."""
        return random.choice(cls.VIEWPORTS)

    @classmethod
    def get_random_timezone(cls) -> str:
        """Get a random timezone."""
        return random.choice(cls.TIMEZONES)


def create_stealth_context(playwright, proxy: str = None) -> BrowserContext:
    """
    Create a browser context with stealth settings.

    Args:
        playwright: Playwright instance
        proxy: Optional proxy server (format: "http://host:port")

    Returns:
        Stealth-configured browser context
    """

    # Random configuration
    user_agent = StealthConfig.get_random_user_agent()
    viewport = StealthConfig.get_random_viewport()
    timezone = StealthConfig.get_random_timezone()

    # Browser args for stealth
    browser_args = [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
    ]

    # Launch browser
    browser = playwright.chromium.launch(
        headless=True,
        args=browser_args
    )

    # Context options
    context_options = {
        "user_agent": user_agent,
        "viewport": viewport,
        "locale": "en-US",
        "timezone_id": timezone,
        "permissions": ["geolocation"],
        "color_scheme": "light",
        "extra_http_headers": {
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    }

    # Add proxy if provided
    if proxy:
        context_options["proxy"] = {"server": proxy}

    context = browser.new_context(**context_options)

    return context


def apply_stealth_scripts(page: Page):
    """
    Apply stealth JavaScript to hide automation.

    Args:
        page: Playwright page instance
    """

    # Override navigator.webdriver
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    # Override navigator.plugins
    page.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
    """)

    # Override navigator.languages
    page.add_init_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)

    # Override chrome property
    page.add_init_script("""
        window.chrome = {
            runtime: {}
        };
    """)

    # Override permissions
    page.add_init_script("""
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)

    # Make iframe contentWindow accessible
    page.add_init_script("""
        Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
            get: function() {
                return window;
            }
        });
    """)

    # Add realistic mouse movements
    page.add_init_script("""
        // Simulate natural mouse movement
        let mouseX = 0;
        let mouseY = 0;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        // Random mouse movements
        setInterval(() => {
            const event = new MouseEvent('mousemove', {
                clientX: mouseX + Math.random() * 10 - 5,
                clientY: mouseY + Math.random() * 10 - 5
            });
            document.dispatchEvent(event);
        }, 100);
    """)


async def human_like_delay(min_ms: int = 100, max_ms: int = 300):
    """
    Add a human-like random delay.

    Args:
        min_ms: Minimum delay in milliseconds
        max_ms: Maximum delay in milliseconds
    """
    import asyncio
    delay = random.randint(min_ms, max_ms) / 1000
    await asyncio.sleep(delay)


def random_mouse_movement(page: Page):
    """Simulate random mouse movements."""
    import random

    # Move mouse to random positions
    for _ in range(random.randint(2, 5)):
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        page.mouse.move(x, y)


def human_type(page: Page, selector: str, text: str):
    """
    Type text with human-like delays.

    Args:
        page: Playwright page
        selector: Element selector
        text: Text to type
    """
    import time

    element = page.locator(selector)
    element.click()

    for char in text:
        element.type(char, delay=random.randint(50, 150))
        time.sleep(random.uniform(0.05, 0.15))
