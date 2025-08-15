"""High-level LinkedIn scraping session API."""

from playwright.async_api import Page

from .auth import CookieAuth, LinkedInAuth, PasswordAuth
from .browser import BrowserContextManager
from .models.person import Person


class LinkedInSession:
    """High-level LinkedIn scraping session that manages authentication and browser state."""

    def __init__(self, auth: LinkedInAuth, headless: bool = True):
        """Initialize LinkedIn session parameters.

        Args:
            auth: Authentication instance (PasswordAuth, CookieAuth, etc.)
            headless: Whether to run browser in headless mode
        """
        self._auth = auth
        self._headless = headless
        self._browser_session = None
        self._context = None
        self._page = None
        self._authenticated = False

    @classmethod
    def from_password(
        cls, email: str, password: str, interactive: bool = False, headless: bool = True
    ) -> "LinkedInSession":
        """Convenience method to create session with password authentication.

        Args:
            email: LinkedIn email address
            password: LinkedIn password
            interactive: If True, pause for manual captcha/challenge solving
            headless: Whether to run browser in headless mode

        Returns:
            LinkedInSession instance
        """
        auth = PasswordAuth(email, password, interactive=interactive)
        return cls(auth, headless=headless)

    @classmethod
    def from_cookie(cls, cookie: str, headless: bool = True) -> "LinkedInSession":
        """Convenience method to create session with cookie authentication.

        Args:
            cookie: LinkedIn li_at cookie value
            headless: Whether to run browser in headless mode

        Returns:
            LinkedInSession instance
        """
        auth = CookieAuth(cookie)
        return cls(auth, headless=headless)

    def is_authenticated(self) -> bool:
        """Check if session is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated and self._page is not None

    def _ensure_authenticated(self) -> Page:
        """Ensure session is authenticated and return page.

        Returns:
            Authenticated page instance

        Raises:
            RuntimeError: If not authenticated
        """
        if not self.is_authenticated():
            raise RuntimeError(
                "Not authenticated. Call login() or login_with_cookie() first."
            )
        if self._page is None:
            raise RuntimeError(
                "No page found. Call login() or login_with_cookie() first."
            )
        return self._page

    async def get_profile(self, url: str) -> Person:
        """Get LinkedIn profile data.

        Args:
            url: LinkedIn profile URL

        Returns:
            Person object with scraped profile data

        Raises:
            RuntimeError: If not authenticated
        """
        from .scrapers.person import PersonScraper

        page: Page = self._ensure_authenticated()
        scraper: PersonScraper = PersonScraper(page)
        return await scraper.scrape_profile(url)

    async def get_company(self, url: str) -> dict:
        """Get LinkedIn company data.

        Args:
            url: LinkedIn company URL

        Returns:
            Company data dictionary

        Raises:
            RuntimeError: If not authenticated
        """
        raise NotImplementedError("Company scraping not yet implemented")

    async def search_jobs(
        self, keywords: str, location: str = "", limit: int = 25
    ) -> list:
        """Search for jobs on LinkedIn.

        Args:
            keywords: Job search keywords
            location: Job location (optional)
            limit: Maximum number of jobs to return

        Returns:
            List of job dictionaries

        Raises:
            RuntimeError: If not authenticated
        """
        raise NotImplementedError("Job search not yet implemented")

    async def close(self) -> None:
        """Close LinkedIn session and clean up browser resources."""
        self._authenticated = False
        if self._browser_session:
            await self._browser_session.__aexit__(None, None, None)
            self._browser_session = None
        self._context = None
        self._page = None

    async def __aenter__(self):
        """Context manager entry - initialize browser and authenticate."""
        try:
            self._browser_session = BrowserContextManager(headless=self._headless)
            self._context = await self._browser_session.__aenter__()
            self._page = await self._auth.login(context=self._context)
            self._authenticated = True
            return self
        except Exception:
            # Clean up on failure
            if self._browser_session:
                await self._browser_session.__aexit__(None, None, None)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        await self.close()
