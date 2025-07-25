from abc import ABC, abstractmethod

from playwright.sync_api import BrowserContext, Page


class LinkedInAuth(ABC):
    """Base class for LinkedIn authentication methods."""

    def __init__(self):
        """Initialize authentication."""
        self._page: Page | None = None

    @abstractmethod
    def _authenticate(self, page: Page) -> bool:
        """Internal authentication method to be implemented by subclasses.

        Args:
            page: Playwright page instance

        Returns:
            True if authentication successful, False otherwise

        Raises:
            Various authentication-specific exceptions
        """
        pass

    def authenticate(self, page: Page) -> bool:
        """Authenticate with LinkedIn.

        Args:
            page: Playwright page instance

        Returns:
            True if authentication successful, False otherwise

        Raises:
            Various authentication-specific exceptions
        """
        self._page = page
        return self._authenticate(page)

    def login(self, context: BrowserContext) -> Page:
        """Convenience method to login and return the authenticated page.

        Args:
            context: Browser context instance

        Returns:
            Authenticated page instance

        Raises:
            Exception if authentication fails
        """
        # Customize context for auth-specific needs
        self._customize_context(context)
        page = context.new_page()

        if not self.authenticate(page=page):
            raise Exception("Authentication failed")
        if self._page is None:
            raise Exception("Page is None after authentication")
        return self._page

    def _customize_context(self, context: BrowserContext):
        """Customize context for auth-specific needs.

        Args:
            context: Browser context instance
        """
        # Default implementation does nothing
        pass

    def is_logged_in(self, page: Page) -> bool:
        """Check if already logged in by looking at current URL and page elements.

        Args:
            page: Playwright page instance

        Returns:
            True if logged in, False otherwise
        """
        try:
            current_url = page.url

            # Check if we're on a login page
            if "login" in current_url:
                return False

            # Check if we're on authenticated pages
            if any(
                indicator in current_url
                for indicator in ["/feed/", "/in/", "/mynetwork", "/jobs"]
            ):
                return True
            return False
        except Exception:
            return False
