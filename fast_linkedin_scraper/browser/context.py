"""Simple browser management for LinkedIn scraping."""

from playwright.async_api import BrowserContext, async_playwright

from ..config import BrowserConfig


class BrowserContextManager:
    """Context manager for browser contexts with automatic cleanup."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright_context = None

    async def __aenter__(self) -> BrowserContext:
        """Create and return browser context with standard configuration."""
        self.playwright_context = async_playwright()
        playwright = await self.playwright_context.__aenter__()

        browser = await playwright.chromium.launch(
            headless=self.headless,
            args=BrowserConfig.CHROME_ARGS,
            channel="chrome",
        )

        context = await browser.new_context(
            user_agent=BrowserConfig.USER_AGENT,
            viewport=BrowserConfig.VIEWPORT,
        )
        context.set_default_timeout(BrowserConfig.TIMEOUT)

        return context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensure browser and playwright are properly closed."""
        if self.playwright_context:
            await self.playwright_context.__aexit__(exc_type, exc_val, exc_tb)
