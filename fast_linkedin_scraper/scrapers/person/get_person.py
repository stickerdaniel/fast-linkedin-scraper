"""Main person profile scraper using Playwright."""

from playwright.async_api import Page
from pydantic import HttpUrl

from ...config import ScrapingFields
from ...models.person import Person
from .accomplishments import scrape_accomplishments
from .contacts import scrape_contacts
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

    async def scrape_profile(
        self, url: str, fields: ScrapingFields = ScrapingFields.MINIMAL
    ) -> Person:
        """Scrape a LinkedIn person profile.

        Args:
            url: LinkedIn profile URL as string
            fields: ScrapingFields enum specifying which fields to scrape

        Returns:
            Person model with scraped data
        """
        # Validate URL
        linkedin_url = HttpUrl(url)

        # Navigate to profile
        await self.page.goto(str(linkedin_url))

        # Wait for initial content to load
        await self.page.wait_for_timeout(2000)  # 2 seconds

        # Initialize Person model
        person = Person(linkedin_url=linkedin_url)

        # Authentication is already handled by the session that passed us the page

        # Always scrape basic information (it's on the main page)
        if ScrapingFields.BASIC_INFO in fields:
            await self._scrape_basic_info(person)
            await self.page.wait_for_timeout(1000)  # 1 second between sections

        # Conditionally scrape other fields
        if ScrapingFields.EXPERIENCE in fields:
            await scrape_experiences(self.page, person)
            await self.page.wait_for_timeout(1000)  # 1 second between sections

        if ScrapingFields.EDUCATION in fields:
            await scrape_educations(self.page, person)
            await self.page.wait_for_timeout(1000)  # 1 second between sections

        if ScrapingFields.INTERESTS in fields:
            await scrape_interests(self.page, person)
            await self.page.wait_for_timeout(1000)  # 1 second between sections

        if ScrapingFields.ACCOMPLISHMENTS in fields:
            await scrape_accomplishments(self.page, person)
            await self.page.wait_for_timeout(1000)  # 1 second between sections

        if ScrapingFields.CONTACTS in fields:
            await scrape_contacts(self.page, person)
            await self.page.wait_for_timeout(1000)  # 1 second between sections

        return person

    async def _scrape_basic_info(self, person: Person) -> None:
        """Scrape basic profile information (name, location, about)."""
        # Get name and location
        try:
            top_panel = self.page.locator(".mt2.relative").first
            name_element = top_panel.locator("h1").first
            if await name_element.is_visible():
                person.name = await name_element.inner_text()
        except Exception:
            pass

        try:
            location_element = self.page.locator(
                ".text-body-small.inline.t-black--light.break-words"
            ).first
            if await location_element.is_visible():
                person.add_location(await location_element.inner_text())
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
                if await headline_element.is_visible():
                    headline_text = (await headline_element.inner_text()).strip()
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
            if await about.is_visible():
                about_text = await about.inner_text()
                person.add_about(about_text)
        except Exception:
            pass

        # Check if open to work
        try:
            profile_picture = self.page.locator(
                ".pv-top-card-profile-picture img"
            ).first
            if await profile_picture.is_visible():
                title_attr = await profile_picture.get_attribute("title")
                person.open_to_work = title_attr and "#OPEN_TO_WORK" in title_attr
        except Exception:
            person.open_to_work = False
