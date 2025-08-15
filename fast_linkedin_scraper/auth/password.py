from playwright.async_api import Page

from ..exceptions import (
    InvalidCredentialsError,
    LoginTimeoutError,
    SecurityChallengeError,
)
from .base import LinkedInAuth


class PasswordAuth(LinkedInAuth):
    """Password-based LinkedIn authentication."""

    def __init__(self, email: str, password: str, interactive: bool = False):
        """Initialize password authentication.

        Args:
            email: LinkedIn email address
            password: LinkedIn password
            interactive: If True, pause for manual captcha/challenge solving
        """
        super().__init__()
        self.email = email
        self.password = password
        self.interactive = interactive

    async def _authenticate(self, page: Page) -> bool:
        """Authenticate using email and password.

        Args:
            page: Playwright page instance

        Returns:
            True if authentication successful

        Raises:
            InvalidCredentialsError: Wrong email/password combination
            CaptchaRequiredError: CAPTCHA verification required
            SecurityChallengeError: Security challenge required
            TwoFactorAuthError: Two-factor authentication required
            LoginTimeoutError: Login process timed out
        """
        try:
            # Navigate to login page
            await page.goto("https://www.linkedin.com/login")

            # Fill in credentials using ID selectors
            email_input = page.locator("#username")
            await email_input.clear()
            await email_input.fill(self.email)

            # Fill in password
            password_input = page.locator("#password")
            await password_input.clear()
            await password_input.fill(self.password)

            # Submit the form using keyboard
            await password_input.press("Enter")

            # Handle post-login scenarios
            return await self._handle_post_login_scenarios(page, self.interactive)

        except Exception as e:
            raise LoginTimeoutError(f"Login failed: {str(e)}") from e

    async def _handle_post_login_scenarios(
        self, page: Page, interactive: bool = False, interactive_timeout: int = 3000
    ) -> bool:
        """Handle various post-login scenarios and errors."""

        current_url = page.url
        # Check for specific error conditions
        if (
            "challenge" in current_url
            or "checkpoint" in current_url
            or await page.locator("text=security challenge").count() > 0
        ):
            if interactive:
                print(
                    "⚠️  Security challenge/checkpoint detected. Please solve it manually."
                )
                try:
                    input("Press Enter after completing the security challenge...")
                except EOFError:
                    print(
                        f"⏳ Waiting {interactive_timeout} ms for manual completion..."
                    )
                    await page.wait_for_timeout(interactive_timeout)
                return await self.is_logged_in(page)
            else:
                raise SecurityChallengeError(
                    "Security challenge required - enable interactive mode"
                )

        if await self.is_logged_in(page):
            return True

        # Check for invalid credentials # TODO: check correct error message
        error_selectors = [
            "text=Wrong email or password",
        ]
        for selector in error_selectors:
            if await page.locator(selector).count() > 0:
                raise InvalidCredentialsError("Invalid email or password")

        # If we're still on login page, something went wrong
        raise LoginTimeoutError("Login failed - still on login page")
