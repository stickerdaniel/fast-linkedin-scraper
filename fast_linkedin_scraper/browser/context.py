"""Simple browser management for LinkedIn scraping."""

from playwright.sync_api import BrowserContext, sync_playwright

from ..config import BrowserConfig


class BrowserContextManager:
    """Context manager for browser contexts with automatic cleanup."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright_context = None

    def __enter__(self) -> BrowserContext:
        """Create and return browser context with standard configuration."""
        self.playwright_context = sync_playwright()
        playwright = self.playwright_context.__enter__()

        browser = playwright.chromium.launch(
            headless=self.headless,
            args=BrowserConfig.CHROME_ARGS,
            channel="chrome",
        )

        context = browser.new_context(
            user_agent=BrowserConfig.USER_AGENT,
            viewport=BrowserConfig.VIEWPORT,
        )
        context.set_default_timeout(BrowserConfig.TIMEOUT)

        return context

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure browser and playwright are properly closed."""
        if self.playwright_context:
            self.playwright_context.__exit__(exc_type, exc_val, exc_tb)
