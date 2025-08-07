"""Main person profile scraper using Playwright."""

from playwright.sync_api import Page
from pydantic import HttpUrl

from ...models.person import Person
from .accomplishments import scrape_accomplishments
from .education import scrape_educations
from .experience import scrape_experiences
from .interests import scrape_interests


class PersonScraper:
    """Scraper for LinkedIn person profiles."""

    def __init__(self, page: Page):
        """Initialize the scraper with a Playwright page.

        Args:
            page: Authenticated Playwright page instance
        """
        self.page = page

    def scrape_profile(self, url: str) -> Person:
        """Scrape a LinkedIn person profile.

        Args:
            url: LinkedIn profile URL as string

        Returns:
            Person model with scraped data
        """
        # Validate URL
        linkedin_url = HttpUrl(url)

        # Navigate to profile
        self.page.goto(str(linkedin_url))

        # Wait for initial content to load
        self.page.wait_for_timeout(2000)  # 2 seconds

        # Initialize Person model
        person = Person(linkedin_url=linkedin_url)

        # Authentication is already handled by the session that passed us the page

        # Scrape basic information
        self._scrape_basic_info(person)
        self.page.wait_for_timeout(1000)  # 1 second between sections

        # Scrape experiences
        scrape_experiences(self.page, person)
        self.page.wait_for_timeout(1000)  # 1 second between sections

        # Scrape educations
        scrape_educations(self.page, person)
        self.page.wait_for_timeout(1000)  # 1 second between sections

        # Scrape interests
        scrape_interests(self.page, person)
        self.page.wait_for_timeout(1000)  # 1 second between sections

        # Scrape accomplishments
        scrape_accomplishments(self.page, person)
        self.page.wait_for_timeout(1000)  # 1 second between sections

        # # Scrape connections
        # scrape_connections(self.page, person)

        return person

    def _scrape_basic_info(self, person: Person) -> None:
        """Scrape basic profile information (name, location, about)."""
        # Get name and location
        try:
            top_panel = self.page.locator(".mt2.relative").first
            name_element = top_panel.locator("h1").first
            if name_element.is_visible():
                person.name = name_element.inner_text()
        except Exception:
            pass

        try:
            location_element = self.page.locator(
                ".text-body-small.inline.t-black--light.break-words"
            ).first
            if location_element.is_visible():
                person.add_location(location_element.inner_text())
        except Exception:
            pass

        # Get headline - simplified approach based on DOM structure
        try:
            # From MCP DOM analysis, the headline appears right after the name
            # Try multiple selectors that should work universally
            headline_selectors = [
                # Direct approach: find h1 then get the next generic element
                "h1 + div",
                "h1 ~ div:first-of-type",
                # Alternative: look in the main profile section
                ".mt2.relative div:has(h1) + div",
                # Fallback: find elements that typically contain headlines
                ".pv-text-details__left-panel > div:nth-child(2)",
                ".pv-top-card-v2-section-info > div:nth-child(2)",
            ]

            for selector in headline_selectors:
                headline_element = self.page.locator(selector).first
                if headline_element.is_visible():
                    headline_text = headline_element.inner_text().strip()
                    # Make sure it's not the name and has substantial content
                    if (
                        headline_text
                        and headline_text != person.name
                        and len(headline_text) > 5
                        and headline_text not in ["", "null", "undefined"]
                    ):
                        person.add_headline(headline_text)
                        break
        except Exception:
            pass

        # Get about section - following Selenium approach exactly
        try:
            about = (
                self.page.locator("#about").locator("..").locator(".display-flex").first
            )
            if about.is_visible():
                about_text = about.inner_text()
                person.add_about(about_text)
        except Exception:
            pass

        # Check if open to work
        try:
            profile_picture = self.page.locator(
                ".pv-top-card-profile-picture img"
            ).first
            if profile_picture.is_visible():
                title_attr = profile_picture.get_attribute("title")
                person.open_to_work = title_attr and "#OPEN_TO_WORK" in title_attr
        except Exception:
            person.open_to_work = False
